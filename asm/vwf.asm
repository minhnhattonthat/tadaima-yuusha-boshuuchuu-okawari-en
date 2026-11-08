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
!IMAGES = $E20000       ; far number -> u24 tiles, tile count (tools/insert.py)
!POOL   = $4A           ; old kana tiles the names go to, up to !POOLEND; $30-$49 hold a-z, the game's own mapping sends $24-$3D there
!POOLEND = $A0
!NAMEBUF = $7FFF30      ; 5 name bytes + FF for strip
!HEAD   = $7FFF24       ; next free pool tile
!NEXT   = $7FFF25       ; next tile to give out
!RUN    = $7FFF26       ; tiles left to give out
!SKIP   = $7FFF27       ; number bytes still to come
!NUM    = $7FFF28
!RECP   = $7FFF2A       ; next upload record
; The scheduler's 5 bytes of a continuation record must be in bank 0. $1538-$154A: no scene of the original's tour
; writes it (tools/debug/lowmap.lua + freeram.py) and no absolute operand names it. $0483 was the sprite buffer's tail.
!RECORDS = $1538
!RECSIZE = 6
!RECN   = 3
!PAY    = $7FFF40       ; per record, 12 apart: +0 source, +2 bank, +3 tile count, +4 VRAM word, +6 busy until sent

; ------ hooks: every overwritten instruction is listed in docs/re/vwf.md
org $C2143B
    jml far_read
org $C21780
    jml vwf_char
org $C21AC4
    jml strip

org $C21A99
    jml text_wait

org $C21E93
    jml small_map
org $C220BD
    jml small_end
org $C21CF0
    jml rect_read
org $C2A63F
    jml top_name
; "12/25 うまれ" is built from immediates, three tiles of the label sheet (rects.tiles): DOB
org $C2BD6C
    dw $190E
org $C2BD72
    dw $000C

org $C0FFD7
    db $0C              ; 4 MB

org $E00000
; $80E11C(id) sleeps until something signals id ($80E14D): 1 = next frame, 6 = the input poll ($82:93BE), which is what a window's
; +01 holds, and that comes about every 6 frames. English has 2-3 times the glyphs of the Japanese, so the two waits per letter
; (return addresses below, minus one) sleep by frames instead. Everything else keeps id 6: the page prompt's loop must stay in step with
; the poll or it misses presses, including its own glyph draw ($0FB8 set), and {pause} keeps its length.
text_wait:
    lda 1,s
    cmp.w #$160B        ; speed loop
    beq .fast
    cmp.w #$1818        ; after a glyph
    bne .poll
    lda.l $7E0FB8
    beq .fast
.poll:
    lda.w $0001,x
    and.w #$00FF
    bra .wait
.fast:
    jsl $80E113
    lda.w #$0001        ; about 3 frames a letter, 20 a second
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
    pha                 ; page or newline: the open cell stays on the old line, and the page arrow goes after it, not over it
    jsr align
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

; Tile-rect blit: a record starting F0 lo hi is a far rect, a W no record has. The blit reads it with DB switched; everything else it touches is low RAM or long.
rect_read:
    phy
    ldy.w $11ED
    lda.w $0000,y
    and.w #$00FF
    cmp.w #!FAR
    beq rect_read_far
    ply
rect_body:
    lda $00
    pha
    lda $02
    pha
    jml $C21CF6
rect_read_far:
    lda $00
    pha
    lda.w $0001,y
    jsr far_entry
    tya
    sta.w $11ED
    lda 2,s             ; $00 went on far_entry's stack shuffle
    sta $00
    jsl rect_body
    plb
    pla
    ply
    rtl

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
    phy
    jsr clear_cells
    ply
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
    bne +
    rts
+
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
    cmp.w #$00F5        ; {cell}: end the open cell, or a blank cell if none is open. Word slots in a sheet of cells line up on it
    bne +
    lda.l !PEN
    beq .blank
    jsr strip_flush
    bra strip_text
.blank:
    lda.w #$00F5
    bra .fixed
+
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
    jmp strip_text
.far:
    lda.w $0000,y
    jsr far_entry
    jsr strip_text
    plb
.ret:
    rts

; $C2A63F: 5 cells of label, then 5 of name, read one glyph at a time. Both go through strip so English draws.
top_name:
    ldx.w #$0000
    lda.w #$0000
.clear:
    sta.l $7E7900,x
    inx
    inx
    cpx.w #$0500
    bne .clear
    lda $0A             ; strip counts in $0A
    pha
    ldy.w #$B220
    ldx.w #$7900
    jsl strip
    pla
    sta $0A
    ldy.w #$0000
.copy:
    lda ($0A),y
    tyx
    sta.l !NAMEBUF,x
    iny
    cpy.w #$0005
    bne .copy
    lda.w #$00FF
    sta.l !NAMEBUF+5
    phb
    pea.w $7F7F
    plb
    plb
    ldy.w #!NAMEBUF
    ldx.w #$7B80
    jsl strip
    plb
    jml $C2A66F

; bufA goes to the strip, bufB moves down
strip_flush:
    phy
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
    jsr shift_cells
    ply
    rts

; ------ the tilemap path: $C21E93 turns a code into a tile pair, every loop that draws small text calls it per byte. A far code there shows
; its name as tiles made at build time: sent into the old kana tiles (a ring, a name stays as long as nothing else draws 95 tiles), and
; each byte of the string gives the next tile. A = upper row (blank), B = lower row.
small_map:
    cmp.b #!FAR
    beq .far
    pha
    lda.l !SKIP
    beq .text
    dec
    sta.l !SKIP
    bne .lo
    pla
    sta.l !NUM+1
    jsr small_load
    bra .emit
.lo:
    pla
    sta.l !NUM
    bra .emit
.text:
    lda.l !RUN
    beq .plain
    pla
    cmp.b #$F4          ; padding: the rest of the name
    beq .emit
    pha
    lda.b #$00
    sta.l !RUN
.plain:
    pla
    cmp.b #$23
    beq .low
    bcs .high
.low:
    jml $C21E99
.high:
    jml $C21EA2
.far:
    lda.b #$02
    sta.l !SKIP
    inc
    sta.l !RUN
    lda.l !HEAD
    cmp.b #!POOLEND-12  ; room for the longest name
    bcs +
    cmp.b #!POOL        ; WRAM at boot holds anything
    bcs ++
+
    lda.b #!POOL
++
    sta.l !HEAD
    sta.l !NEXT
.emit:
    lda.l !RUN
    beq .blank
    dec
    sta.l !RUN
    lda.l !NEXT
    inc
    sta.l !NEXT
    dec
    bra .pair
.blank:
    lda.b #$00
.pair:
    pha                 ; two callers add a font offset to what we return: take it back
    rep #$20
    lda 2,s
    cmp.w #$1E77
    beq .sub02
    cmp.w #$20C4
    beq .sub0A
    sep #$20
    pla
    bra .done
.sub02:
    sep #$20
    pla
    sec
    sbc $02
    bra .done
.sub0A:
    sep #$20
    pla
    sec
    sbc $0A
.done:
    xba
    lda.b #$26
    rtl

; the loop that stops at FE/FF: a name may run past the old string
small_end:
    cmp.b #$FE
    bcs +
    jml $C220C1
+
    pha
    lda.l !RUN
    beq .stop
    pla
    lda.b #$F4
    jsl small_map
    sta ($04),y
    xba
    sta ($02),y
    iny
    jml $C220BB
.stop:
    pla
    jml $C220D6

; A8. Number complete: RUN = its tiles left after the two already given out, HEAD moves on, tiles sent in the next VBlank.
small_load:
    php
    rep #$30
    phb
    phd
    phx
    phy
    pea.w $8080
    plb
    plb
    lda.w #$0000
    tcd
.wait:
    lda.w $0166         ; continuations waiting: a frame's VBlank holds about 8 names
    and.w #$00FF
    cmp.w #$0008
    bcc +
    jsl $80E113         ; sleep a frame: the queue drains in this scheduler, a spin never sees it move
    lda.w #$0001
    jsl $80E11C
    bra .wait
+
    lda.l !NUM
    asl
    asl
    tax
    lda.l !RECP
    cmp.w #!RECORDS
    bcc +
    cmp.w #!RECORDS+(!RECSIZE*!RECN)  ; asar math runs left to right: without the brackets the ring never wrapped
    bcc ++
+
    lda.w #!RECORDS
++
    tay
    jsr pay_index       ; A is still the record
    phx
    tax
    lda.w #3            ; a record still queued is sent in the next frame; bounded, as WRAM at boot holds anything
.busy:
    pha
    lda.l !PAY+6,x
    and.w #$00FF
    beq .free
    phx
    phy
    jsl $80E113
    lda.w #$0001
    jsl $80E11C
    ply
    plx
    pla
    dec
    bne .busy
    pha
.free:
    pla
    txa
    plx                 ; X = image index, A = payload index
    phy
    tay
    lda.l !IMAGES,x
    phx
    tyx
    sta.l !PAY,x
    plx
    lda.l !IMAGES+2,x   ; bank, tile count
    phx
    tyx
    sta.l !PAY+2,x
    lda.l !HEAD
    and.w #$00FF
    asl
    asl
    asl
    asl
    clc
    adc.w #$4000
    sta.l !PAY+4,x
    lda.w #$0001
    sta.l !PAY+6,x
    plx
    ply
    lda.l !IMAGES+3,x
    and.w #$00FF
    sep #$20
    pha
    dec
    dec
    sta.l !RUN
    pla
    clc
    adc.l !HEAD
    sta.l !HEAD
    rep #$20
    tya
    clc
    adc.w #!RECSIZE
    sta.l !RECP
    tyx
    jsl small_send
    ply
    plx
    pld
    plb
    plp
    rts

; The game's $80D78F: what follows it runs in VBlank with X = record, or now during forced blank.
small_send:
    jsl $80D78F
    txa
    jsr pay_index
    tax
    lda.l !PAY+3,x
    and.w #$00FF
    asl
    asl
    asl
    asl
    asl
    tcd
    lda.l !PAY+4,x
    tay
    lda.w #$0000
    sta.l !PAY+6,x      ; free once this runs: $80D6F5 doesn't wait
    lda.l !PAY+2,x
    and.w #$00FF
    pha
    lda.l !PAY,x
    tax
    pla
    jsl $80D6F5
    rtl

; A16: A = record -> A = payload index, 12 a record.
pay_index:
    sec
    sbc.w #!RECORDS     ; 0, 6, 12 -> 0, 12, 24
    asl
    rts

planebit:
    db 1, 2, 4, 8
tilecol:
    dw 0, 32, 128, 160
width:
    incbin "../build/vwf_width.bin"
font:
    incbin "../build/vwf_font.bin"
assert pc() <= $E08000
