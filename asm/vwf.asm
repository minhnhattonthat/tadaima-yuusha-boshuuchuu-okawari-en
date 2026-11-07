; Far text and variable-width font. docs/re/vwf.md has the design and the hook list.
hirom

!FAR    = $F0           ; text code: F0 lo hi = print far string number hilo, then the string is over
!TABLE  = $E10000       ; far strings: u24 entries, CPU addresses in $A1-$BF:8000+ (low RAM stays visible, the engine needs it)
!BUFA   = $FE00         ; bank $7F, free (tools/debug/ramuse.py): 4bpp 16x16 cell the pen is in
!BUFB   = $FE80         ; the next cell, a glyph spills into it
!PEN    = $7FFF00       ; px inside the cell, 0-15
!WIN    = $7FFF02       ; window record of the open cell
!POS    = $7FFF04       ; its +6 col, +7 row
!FG     = $7FFF06       ; colour
!SH     = $7FFF07       ; shadow colour
!DST    = $7FFF08       ; strip: next cell in bank $7E
!ADV    = $FF0A         ; these in DB $7F, render only
!PREV   = $FF0C
!ROW    = $FF0E
!FM     = $FF10         ; 3 bytes ink mask
!SM     = $FF14         ; 3 bytes shadow mask
!FP     = $FF18         ; 4 bytes $FF/$00 per plane: ink
!SP     = $FF1C         ; shadow
!KEEP   = $FF20
!T      = $FF22

; ------ hooks: every overwritten instruction is listed in docs/re/vwf.md
org $C2143B
    jml far_read
org $C21780
    jml vwf_char
org $C21AC4
    jml strip

org $C21A99
    jml text_wait

org $C0FFD7
    db $0C              ; 4 MB

org $E00000
; A window sleeps +01 frames (6) per glyph and again in the speed loop: English has 2-3 times the glyphs of the Japanese.
; {pause} waits through the same routine and keeps its length.
text_wait:
    lda.w $0001,x
    and.w #$00FF
    pha
    lda 3,s
    cmp.w #$1538        ; return address of the JSR in the pause loop, minus one
    pla
    beq .wait
    lsr                 ; 6 -> 2: a letter takes 4 frames, 15 a second
    beq .one
    dec
    bne .wait
.one:
    lda.w #$0001
.wait:
    jsl $80E11C
    jml $C21AA3

far_read:
    cmp.w #$00FF
    beq .end
    cmp.w #!FAR
    beq .far
    cmp.w #$00FC
    bcc .go
    pha                 ; page or newline: the open cell stays on the old line
    jsr close_cell
    pla
.go:
    jml $C21443
.end:
    jml $C215B9
.far:
    lda.w $0001,y
    jsr far_entry
    jsl $C21421
    plb
    sta $00
    jml $C215B9

; A = string number -> Y = string, DB = its bank. The caller's DB is on the stack: plb when done.
far_entry:
    sta $00
    asl
    clc
    adc $00
    phx
    tax
    lda.l !TABLE,x
    tay
    sep #$20
    lda.l !TABLE+2,x
    plx
    sta $00
    pla                 ; return address under the DB we push
    sta $01
    pla
    phb
    pha
    lda $01
    pha
    lda $00
    pha
    plb
    rep #$20
    rts

; Y flag: Z set when X's window still has its pen here.
same_pos:
    txa
    cmp.l !WIN
    bne .no
    lda.w $0006,x
    cmp.l !POS
.no:
    rts

; +0E is a tile number, a multiple of 4. Bit 0 = this window has an open cell: any code that sets +0E closes it.
close_cell:
    lda.w $000E,x
    bit.w #$0001
    beq next_tile_rts
    and.w #$FFFC
    sta.w $000E,x
next_tile:
    lda.w $0010,x
    clc
    adc.w #$0040
    sta.w $0010,x
    lda.w $000E,x
    clc
    adc.w #$0004
    sta.w $000E,x
    cmp.w $0012,x
    bne next_tile_rts
    lda.w $000C,x
    sta.w $0010,x
    lda.w $000A,x
    sta.w $000E,x
next_tile_rts:
    rts

; a fixed-width glyph or code-drawn text comes next: leave the open cell
align:
    lda.w $000E,x
    bit.w #$0001
    beq .done
    jsr same_pos
    bne .moved
    sep #$20
    inc.w $0006,x
    inc.w $0006,x
    rep #$20
.moved:
    jsr close_cell
.done:
    rts

vwf_char:
    pla
    sta $00
    cmp.w #$000A
    bcc .old
    cmp.w #$006A
    bcc .vwf
.old:
    jsr align
    lda $00
    jml $C21783
.vwf:
    lda.w $000E,x
    bit.w #$0001
    beq .fresh
    jsr same_pos
    beq .keep
    jsr close_cell
.fresh:
    lda.w #$0000
    sta.l !PEN
    jsr clear_cells
    bra .draw
.keep:
    lda.w $000E,x
    and.w #$FFFC
    sta.w $000E,x
.draw:
    lda.w $0014,x
    sta.l !FG
    jsr render
    jsr blit
    lda.l !PEN
    cmp.w #$0010
    bcc .done
    sbc.w #$0010
    sta.l !PEN
    sep #$20
    inc.w $0006,x
    inc.w $0006,x
    rep #$20
    jsr next_tile
    jsr shift_cells
    lda.l !PEN
    beq .done
    sep #$20
    lda.w $0006,x
    cmp.w $0008,x
    rep #$20
    beq .done           ; line full: the lint keeps text off this edge
    jsr blit
.done:
    lda.l !PEN
    beq .closed
    lda.w $000E,x
    ora.w #$0001
    sta.w $000E,x
.closed:
    txa
    sta.l !WIN
    lda.w $0006,x
    sta.l !POS
    rtl

; draw the cell through the game's own code: tilemap, VRAM queue and frame wait
blit:
    phx
    phb
    lda.w #$007F
    ldx.w #!BUFA
    ldy.w #$0FC1
    db $54,$7E,$7F      ; mvn dst $7E, src $7F
    plb
    plx
    lda.w #$0001
    sta.l $7E0FB8       ; $C21819 skips its cell advance
    jsl $C217A2
    lda.w #$0000
    sta.l $7E0FB8
    rts

; bufB -> bufA, clear bufB
shift_cells:
    phx
    phb
    lda.w #$007F
    ldx.w #!BUFB
    ldy.w #!BUFA
    db $54,$7F,$7F
    plb
    plx
    ldy.w #$0080
    bra clear_from
clear_cells:
    ldy.w #$0000
clear_from:
    phx
    tyx
    lda.w #$0000
.loop:
    sta.l $7F0000+!BUFA,x
    inx
    inx
    cpx.w #$0100
    bne .loop
    plx
    rts

; $00 = glyph code, FG/SH set. Draws at PEN into bufA/bufB, moves PEN. Keeps X.
render:
    phx
    phb
    sep #$20
    lda.b #$7F
    pha
    plb
    ldx.w #$0003
.plane:
    lda.w !FG-$7F0000
    and.l planebit,x
    beq +
    lda.b #$FF
+
    sta.w !FP,x
    lda.w !SH-$7F0000
    and.l planebit,x
    beq +
    lda.b #$FF
+
    sta.w !SP,x
    dex
    bpl .plane
    rep #$20
    lda $00
    sec
    sbc.w #$000A
    tax
    lda.l width,x
    and.w #$00FF
    sta.w !ADV
    txa
    asl
    asl
    asl
    asl
    tax
    stz.w !PREV
    stz.w !ROW
.row:
    lda.l font,x
    and.w #$00FF
    xba
    pha
    lsr
    ora.w !PREV
    sta.w !T
    lda.w !PREV
    lsr
    ora.w !T
    sta.w !T
    pla
    sta.w !PREV
    eor.w #$FFFF
    and.w !T
    phx
    pha
    lda.w !PREV
    ldy.w #!FM
    jsr spread
    pla
    ldy.w #!SM
    jsr spread
    lda.w !PEN-$7F0000
    lsr
    lsr
    lsr
    tax                 ; first tile column
    ldy.w #$0000
.col:
    jsr plot
    inx
    iny
    cpy.w #$0003
    bne .col
    plx
    inx
    lda.w !ROW
    inc
    sta.w !ROW
    cmp.w #$000E
    bne .row
    lda.w !ADV
    clc
    adc.w !PEN-$7F0000
    sta.w !PEN-$7F0000
    plb
    plx
    rts

; A = 16 px mask, left pixel in bit 15. Y = where the three bytes go, shifted by PEN & 7.
spread:
    sta.w !T
    phx
    lda.w !PEN-$7F0000
    and.w #$0007
    tax
    lda.w !T
    stz.w !T
    cpx.w #$0000
    beq .done
.shift:
    lsr
    ror.w !T
    dex
    bne .shift
.done:
    sep #$20
    sta.w $0001,y
    xba
    sta.w $0000,y
    lda.w !T+1
    sta.w $0002,y
    rep #$20
    plx
    rts

; X = tile column 0-3 (2, 3 are the next cell), Y = mask byte 0-2. Keeps X, Y.
plot:
    phx
    phy
    sep #$20
    lda.w !FM,y
    ora.w !SM,y
    beq .skip
    eor.b #$FF
    sta.w !KEEP
    rep #$20
    lda.w !ROW
    and.w #$0007
    asl
    sta.w !T
    txa
    asl
    tax
    lda.w !ROW
    cmp.w #$0008
    lda.l tilecol,x
    bcc +
    adc.w #$003F        ; bottom tiles, carry set
+
    clc
    adc.w !T
    tax                 ; X = byte offset of this row in the two cells
    sep #$20
    lda.w !FM,y
    sta.w !T
    lda.w !SM,y
    sta.w !T+1
    ldy.w #$0000
.plane:
    lda.w !BUFA,x
    and.w !KEEP
    sta.w !KEEP+1
    lda.w !FP,y
    and.w !T
    ora.w !KEEP+1
    sta.w !KEEP+1
    lda.w !SP,y
    and.w !T+1
    ora.w !KEEP+1
    sta.w !BUFA,x
    inx
    cpy.w #$0001
    bne +
    rep #$20            ; planes 2, 3 sit 16 bytes on, plane 0's byte + 16 = X + 14 here
    txa
    clc
    adc.w #$000E
    tax
    sep #$20
+
    iny
    cpy.w #$0004
    bne .plane
.skip:
    rep #$20
    ply
    plx
    rts

; String to a run of cells in RAM, as $C21AC4: Y string, X dest, $02/$03 colours. Returns X past the cells, Y cell count.
strip:
    stz $0A
    txa
    sta.l !DST
    lda $02
    sta.l !FG
    lda.w #$0000
    sta.l !PEN
    jsr clear_cells
    jsr strip_text
    lda.l !PEN
    beq +
    jsr strip_flush
+
    lda.l !DST
    tax
    ldy $0A
    rtl

strip_text:
    lda.w $0000,y
    and.w #$00FF
    cmp.w #$00FF
    beq .ret
    iny
    cmp.w #$00FB
    beq .color
    cmp.w #!FAR
    beq .far
    cmp.w #$00F7
    bne .glyph
    lda.w $0000,y
    and.w #$00FF
    ora.w #$0100
    iny
    bra .fixed
.glyph:
    cmp.w #$000A
    bcc .fixed
    cmp.w #$006A
    bcs .fixed
    sta $00
    phy
    jsr render
    ply
    lda.l !PEN
    cmp.w #$0010
    bcc strip_text
    jsr strip_flush
    bra strip_text
.fixed:
    sta $00
    lda.l !PEN
    beq +
    jsr strip_flush
+
    phy
    lda.l !DST
    tax
    jsl $C21B0B
    txa
    sta.l !DST
    inc $0A
    ply
    bra strip_text
.color:
    sep #$20
    lda.w $0000,y
    sta $02
    sta.l !FG
    rep #$20
    iny
    bra strip_text
.far:
    lda.w $0000,y
    jsr far_entry
    jsr strip_text
    plb
.ret:
    rts

; bufA goes to the strip, bufB moves down
strip_flush:
    phb
    lda.l !DST
    tay
    clc
    adc.w #$0080
    sta.l !DST
    lda.w #$007F
    ldx.w #!BUFA
    db $54,$7E,$7F
    plb
    inc $0A
    lda.l !PEN
    sec
    sbc.w #$0010
    bpl +
    lda.w #$0000
+
    sta.l !PEN
    jmp shift_cells

planebit:
    db 1, 2, 4, 8
tilecol:
    dw 0, 32, 128, 160
width:
    incbin "../build/vwf_width.bin"
font:
    incbin "../build/vwf_font.bin"
assert pc() <= $E08000
