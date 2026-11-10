; Far text and variable-width font. docs/re/vwf.md has the design and the hook list.
hirom

!FAR    = $F0           ; text code: F0 lo hi = print far string number hilo, then the string is over
!CALL   = $F1           ; F1 lo hi = the same, then skip F4 padding and go on: place records, where code appends text to the slot
!TABLE  = $E10000       ; far strings: u24 entries, CPU addresses in $A1-$BF:8000+ (low RAM stays visible, the engine needs it)
!BUFA   = $FE00         ; bank $7F, free (tools/debug/ramuse.py): 4bpp 16x16 cell the pen is in
!BUFB   = $FE80         ; the next cell, a glyph spills into it
!PEN    = $7FFF00       ; px inside the cell, 0-15
!INSET  = 4             ; dialogue lines start this many px into their first cell
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
!POOLB  = $7A           ; names ring $4A-$79 (6 names of 8 tiles), description/bio lines ring $7A-$9F (3 lines of 10 and change):
!POOLEND = $A0          ; one ring let a new description overwrite list names still on screen (docs/re/vwf.md)
!ROOM   = 10            ; the longest image: description lines are 10 cells, names fewer
!HEADB  = $7FFF2C       ; next free tile of the lines ring
!RING   = $7FFF2D       ; ring of the image being drawn: 0 names, 1 lines
!NAMEBUF = $7FFF30      ; 5 name bytes + FF for strip
!FIXED  = $7FFF36       ; strip: nonzero = every glyph in its own cell, the original way (fixed_check)
!HEAD   = $7FFF24       ; next free pool tile
!NEXT   = $7FFF25       ; next tile to give out
!RUN    = $7FFF26       ; tiles left to give out
!SKIP   = $7FFF27       ; number bytes still to come
!NUM    = $7FFF28
!RECP   = $7FFF2A       ; next upload record
!CACHE  = $7FFF64       ; names ring images, 4 bytes each: +0 far number, +2 first tile (0 = none), +3 tile count (name_cache)
!CACHEN = 6
!CROT   = $7FFF7C       ; next cache slot x 4
!HIT    = $7FFF7D       ; nonzero: this image goes back into its cached tiles, the ring's head stays
!CFIRST = $7FFF7E
!CEND   = $7FFF7F
!HUDC   = $7FFF2E       ; nonzero: the image being drawn is a HUD panel name (name_cache)
!PANEL  = $7FFF80       ; what each HUD panel shows, 4 bytes an entry: +0 panel key (!PKEY), +2 first tile (0 = none), +3 count
!PANELN = 6             ; (the inn's recruit screen has 5 panels); other names-ring images go past all of them (protect)
!PROT   = $7FFF98       ; next entry x 4 for a new key
!MOVED  = $7FFF99       ; protect: nonzero = this pass moved the start
!NEED   = $7FFF9C       ; tiles the image being placed needs: its own count when the number can be read ahead, else !ROOM
!PKEY   = $7FFF9A       ; 16-bit: the panel being drawn = its face slot, DP $00 & $F0 in $C2:B0F1 (face tiles $100 + 16 x panel;
                        ; its screen position $17B8 moves while a panel slides in)
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
; name entry birthday 01月01日: 月 and 日 are 1x1 rects ($C1:4471, $C1:4487, label-sheet tiles F9, 25): "01/01"
org $C59516
    db $2B              ; ／
org $C59519
    db $00
; player select race rect ($C1:574D, pointers $85:988E) at col 2 row 12: 7-tile Nyankee / Tinnian hit the panel's right border, col 1 clears it
org $C14260
    dw $0001
org $C1535A
    dw $0001
; FE {color:09}危険度{color:07}★★★ after a place record in the map-town box is built from immediates ($C2:D4F7): 危険度 (F7 8C F7 42 F7 C7)
; becomes F1 00 00 F4 F4 F4, a call to far string 0 (insert.CODE_TEXT, always numbered first), the pads skipped
org $C2D504
    dw $00F1
org $C2D50A
    dw $F400
org $C2D510
    dw $F4F4
org $C2D535             ; an unlit star: F5 (skip a cell) left a stale VWF tile there; F4 draws the blank glyph
    db $F4
; shop/inn header 勇者 + name ($C5:5584, F7 00 F7 01 into $1236, the name at $123A, drawn by strip): F1 01 00 F4, far string 1 "Hero "
org $C55585
    dw $01F1
org $C5558B
    dw $F400
; The header shows strip cells 0-1 (勇者) in a fixed rect and cells 2.. in a rect as wide as the name's non-F4 bytes, right-aligned to them:
; a far name (F0 lo hi F4 F4) gave 3, a gap after cell 1. VWF packs "Hero " + name, so always show 5 cells; header_strip blanks the
; 7 cells and uploads all of them (the original drew every pad as a cell; unwritten ones showed stale VRAM after the name)
org $C55665
    db $80              ; bne -> bra: name width 5
org $C555C1
    jsl header_strip
org $C2B67A
    jsl name_strip      ; same stale cells after a hero's name in the status box and equip header

; recruit status box ($C2:B3DD, copied rect $A0DA at $1111): job cells (5x2 at $C0:A09E + 10 * job) and race cells (6x2 at $C0:A056
; + 12 * race) went to two rows each, kana on the lower, dakuten on the upper. English (tools/rects.py CELLS) is lower row only: both
; stores of each loop write the lower row from the entry's first bytes, job 6 cells and race 7 (Knight, Priest; Nyankee, Tinnian),
; both from col 6; the gender glyph moves from col 12 to 13 to make room
org $C2B42A
    dw $112E            ; ♂/♀: row 1, col 13
; battle result box ($C3:38D9): each row is 6 digit cells + a 5-byte label copied from $81:8474/8479/847E into $1A2F/4F/6F.
; シリング becomes a far name (name_result, r018479:6): copy 6 bytes, the 6th is the EXP label's leading F4 pad (player bug report).
; The sprite frame covers cell 11, so the row moves a cell left: label at col 5, digits from $1A4E
; shortcut: the top digit lands in row 0 col 31, off-screen, so 100000+ Shillings in one fight would lose it; widen the frame if that happens
org $C33911
    nop                 ; 5 INY, not 6
org $C33923
    dw $0006
org $C33971
    dw $1A4E
org $C2B44B
    dw $1143            ; job, was upper row $1137 (row 2, col 8)
org $C2B44E
    dw $0000            ; LDA $0005,y -> $0000,y
org $C2B451
    dw $1143            ; row 3, col 6 (was col 8)
org $C2B456
    dw $0006            ; 6 job cells
org $C2B47A
    dw $1127            ; race, was upper row $1119
org $C2B47D
    dw $0000            ; LDA $0006,y -> $0000,y
org $C2B485
    dw $0007            ; 7 race cells (row 1, cols 6-12)

; status box digits ($C2:B7F0 money loop, $C2:B825 years, $C2:B838 months) moved to the English layout (tools/rects.py STATUS_CELLS)
org $C2B7F4
    dw $1113+2          ; row 0, col 2
org $C2B826
    dw $1128+11         ; row 1, col 11
org $C2B839
    dw $1128+16         ; row 1, col 16

; rank label NO・1 ($C2:B76C, tiles of the label sheet): "No.1", o = rects.tiles, ・ redrawn as a stop (font.SMALL_DOT)
org $C2B76D
    dw $3E18

; field HUD bar rank "1位" ($C2:A6DF: INC A / ORA #$FF00 / STA $113E, digit then the 位 tile $FF): "No.1" like the status box
org $C2A6DF
    jsl rank_text
    nop
    nop
    nop

; save slot date "0年目 4月": template rect $85:BC2D (7x1, 年 目 . MM . 月) at col 23, year digits (2) at col 20, month at col 26.
; English "Yr 0 Mo 4": template at col 22 = Y r YY . M o, year at col 24, month at col 29 (tiles of the label sheet, rects.tiles).
; 2 cols right of the JP date so the place name (col 9, rects.REGIONS) gets 12 cells and a gap; month ends at col 30, border at 31
org $C42270
    dw $0016
org $C4236A
    dw $0018
org $C423D1
    dw $001D
org $C5BC2F
    db $23,$41,$00,$00,$00,$17,$3E

; VS-mode date box: $C2:A7E7-A824 built "0年目 4月" in $1236; date_text builds the English
org $C2A7E7
    jsl date_text
    db $80, $C2A825-$C2A7ED   ; bra $C2A825 (asar's bra took only the low byte of this target)

org $C22726             ; JSL $828024: block 4 at boot, then the zeros it no longer holds (boot_block4)
    jsl boot_block4

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
    jsr title_check
    cmp.w #$00FF
    beq .end
    cmp.w #!FAR
    beq .far
    cmp.w #!CALL
    beq .call
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
.call:                  ; $C2:D4AB copies a record into slot $1236, then adds FE 危険度 ★ after its 10 bytes
    phy
    lda.w $0001,y
    jsr far_entry
    jsl $C21421
    plb
    ply
    sta $00
    cmp.w #$0000        ; sta sets no flags
    bne .end            ; skipped or closed: stop like the end code would
-   iny
    lda.w $0002,y       ; the byte after the code
    and.w #$00FF
    cmp.w #$00F4
    beq -
    iny
    iny
    jml $C21421

; Tile-rect blit: a record starting F0 lo hi is a far rect, a W no record has. The blit reads it with DB switched; everything else it touches is low RAM or long.
rect_read:
    jsr rect_room
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

; The blit list at $11D1 holds 11 entries, then its FFFF, then the count $11E9, and the writer never checks. The drain task
; empties it once a game frame; English text makes our frames lag, so the item list queued 12 between drains, the 12th FFFF
; landed on the count and a 0-row entry spun 64 KB DMAs forever (black screen). Full: sleep until the drain has run.
rect_room:
    pha
-   lda.l $7E11E9
    cmp.w #$0016        ; 2 x 11
    bcc +
    jsr nap
    bra -
+   pla
    rts

; Sleep one frame and keep everything the caller had: registers, DB, D and the direct-page scratch $0000-$001F. Other tasks
; use that scratch while we sleep; the game never sleeps inside the routines we hook, so their loop counters live there
; (the item list's row counter $09 was clobbered: rows ran on and overflowed the blit list). shortcut: saves $0000-$001F
; only, so a caller with D != 0 keeps its own page unguarded; widen if a hooked caller turns out to move D.
nap:
    php
    rep #$30
    pha
    phx
    phy
    phb
    phd
    lda.w #$0000
    tcd
    ldx.w #$001E
-   lda $00,x
    pha
    dex
    dex
    bpl -
    jsl $80E113
    lda.w #$0001
    jsl $80E11C
    lda.w #$0000
    tcd
    tax
-   pla
    sta $00,x
    inx
    inx
    cpx.w #$0020
    bne -
    pld
    plb
    ply
    plx
    pla
    plp
    rts

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

; +0E is a tile number: a multiple of 4 plus the window's base (1 in the ending's text window, 0 elsewhere: every window of the tours).
; Bit 1 = this window has an open cell: any code that sets +0E closes it. (Bit 0 was base 1's own bit: the ending drew scrambled cells.)
!OPEN = $0002
close_cell:
    lda.w $000E,x
    bit.w #!OPEN
    beq next_tile_rts
    and.w #$FFFF-!OPEN
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
    bit.w #!OPEN
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

; THE END and CONFIG MODE ($C4:C855-C86A, raw rows, D19) are English in the original's 16 px capitals: while the reader is in them,
; vwf_char sends every glyph down the old path. A = the byte read, kept; Y = its address, DB = its bank.
title_check:
    pha
    phb
    phb
    pla
    and.w #$003F
    cmp.w #$0004
    bne .no
    cpy.w #$C855
    bcc .no
    cpy.w #$C86B
    bcs .no
    lda.w #$0001
    bra +
.no:
    lda.w #$0000
+
    sta.l !FIXED
    pla
    rts

vwf_char:
    pla
    sta $00
    lda.l !FIXED
    bne .old
    lda $00
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
    bit.w #!OPEN
    beq .fresh
    jsr same_pos
    beq .keep
    jsr close_cell
.fresh:
    lda.w $0006,x       ; a line's first cell starts !INSET px in, off the window border (tools/batches.py DLG_PX)
    and.w #$00FF
    beq +
    lda.w #$0000
    bra ++
+
    lda.w #!INSET
++
    sta.l !PEN
    jsr clear_cells
    bra .draw
.keep:
    lda.w $000E,x
    and.w #$FFFF-!OPEN
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
    ora.w #!OPEN
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
    jsr fixed_check
    jsr strip_text
    lda.w #$0000
    sta.l !FIXED
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
    bne +
    jmp .color
+
    cmp.w #!FAR
    bne +
    jmp .far
+
    cmp.w #!CALL        ; far string, then skip F4 pads and go on (a place record's FF FF ends it there)
    bne +
    jmp .call
+
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
    sta $00
    lda.l !FIXED
    beq +
    lda $00
    bra .fixed
+
    lda $00
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
    jmp strip_text
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
.call:
    phy
    lda.w $0000,y
    jsr far_entry
    jsr strip_text
    plb
    ply
    iny
    iny
.pad:
    lda.w $0000,y
    and.w #$00FF
    cmp.w #$00F4
    beq +
    jmp strip_text
+
    iny
    bra .pad

; Glyph sets, not text: the player select draws each byte into its own 16 px cell and a tilemap ($C5:948A) picks cells
; ("PLAYERSCT" becomes PLAYER SELECT in the old big letters). Packed by the VWF they came out garbled, so strings at these
; addresses (any bank mirror) draw every glyph the original way ($C21B0B). Y = string, DB = its bank.
fixed_check:
    phb
    phb
    pla
    and.w #$003F
    cmp.w #$0005
    bne .no
    cpy.w #$9471
    beq .yes
    cpy.w #$947C
    bne .no
.yes:
    lda.w #$0001
    bra +
.no:
    lda.w #$0000
+
    sta.l !FIXED
    rts

; $C21AA4 (strip, then DMA what it wrote) for a slot of N cells the screen always shows: the N cells blanked first and all N sent.
; VWF writes fewer cells than the original's one per byte, and the rest showed stale VRAM. X = cells (bank $7E), Y = string,
; $00 = VRAM word, $02 = colours, as the caller set them.
header_strip:           ; $C5:55C1 shop/inn header: 勇者 + 5 name cells
    lda.w #$0380
    bra strip_n
name_strip:             ; $C2:B67A status box / equip header: a hero's 5 name cells
    lda.w #$0280
strip_n:
    phx
    clc
    adc 1,s
    pha                 ; end of the cells, start
.clear:
    lda.w #$0000
    sta.l $7E0000,x
    inx
    inx
    txa
    cmp 1,s
    bne .clear
    lda 3,s
    tax
    lda $00
    pha
    phx                 ; as the wrapper: VRAM, start
    jsl $C21AC4
    plx
    stx $00
    lda 3,s             ; the end, not strip's X
    sec
    sbc $00
    tcd
    tya
    ply                 ; VRAM
    sta 3,s             ; strip's count over the start
    pla                 ; drop the end
    lda.w #$007E
    jsl $829FDC
    jsl $80E113
    ply
    rtl

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
; each byte of the string gives the next tile. A = lower row (the letter), B = upper row (blank).
small_map:
    cmp.b #!FAR
    beq .far
    cmp.b #!CALL
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
    brl .emit
.lo:
    pla
    sta.l !NUM
    brl .emit
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
    rep #$20
    lda 1,s             ; called from the FE/FF loop ($C220C1): description and bio lines, their own ring
    cmp.w #$20C4
    bne +
    lda 4,s             ; but the equip screen's gear names ($C2:C0CA calls the loop) share the screen with a 3-line bio:
    cmp.w #$C0CD        ; names ring (tools/debug/farcaller.lua)
    beq +
    cmp.w #$B70C        ; and the rank panel's names ($C2:B709), on screen beside the status page's lines (name_cache .rank)
    beq +
    sep #$20
    bra .ringb
+
    sep #$20
    lda.b #$00
    sta.l !RING
    lda.l !HEAD
    cmp.b #!POOLB-!ROOM ; room for the longest image
    bcs +
    cmp.b #!POOL        ; WRAM at boot holds anything
    bcs ++
+
    lda.b #!POOL
++
    sta.l !HEAD
    jsr name_cache
    bra .ready
.ringb:
    lda.b #$01
    sta.l !RING
    lda.l !HEADB
    cmp.b #!POOLEND-!ROOM
    bcs +
    cmp.b #!POOLB
    bcs ++
+
    lda.b #!POOLB
++
    sta.l !HEADB
.ready:
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
.pair:                  ; as the game's own exit ($C2209C XBA): A = lower row (the letter), B = upper row ($26, callers add their font offset)
    xba
    lda.b #$26
    xba
    rtl

; the loop that stops at FE/FF: a name may run past the old string
small_end:
    cmp.b #$FE
    bcs +
    cmp.b #$F4          ; a pad once the row is full (Y - $08 >= width $06): skip it, else its upper-row blank lands on the next line
    bne .map
    pha
    tya
    sec
    sbc $08
    cmp $06
    pla
    bcc .map
    rep #$20
    inc $00
    sep #$20
    jml $C220BB
.map:
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
    clc
    adc $0A
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
    jsr nap             ; sleep a frame: the queue drains in this scheduler, a spin never sees it move
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
    jsr nap
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
    lda.l !NEXT         ; the image's first tile: two tiles were given out before the number was complete
    dec
    dec
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
    adc.l !NEXT
    dec
    dec                 ; first tile + count: the ring's next free tile
    pha
    lda.l !RING
    bne +
    pla
    jsr cache_put
    bra ++
+
    pla
    sta.l !HEADB
++
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

; A8 = HEAD -> A8 = the image's first tile. The HUD panels ($82:B0F1 -> wrapper $C21E8A, DB:Y = character record, the name's far
; number at +2) redraw every candidate's name on each cursor move in the inn's recruit list: each copy took new ring tiles and walked
; over names still on screen (the hero's, drawn once; player bug report). A name already in the ring goes back into its own tiles,
; uploaded again, so a screen that reloaded the sheet meanwhile still gets it. The first two tiles are given out before the number is
; complete, which is why only a caller whose string can be read ahead is matched here.
name_cache:
    php
    rep #$30
    phx
    sep #$20
    sta.l !CFIRST
    lda.b #$00
    sta.l !HIT
    sta.l !HUDC
    lda.b #!ROOM
    sta.l !NEED
    rep #$20
    lda 6,s             ; 1-2 X, 3 P, 4-5 rts, 6-8 small_map's return into the wrapper, 9-11 the wrapper's return
    cmp.w #$1E8F
    beq +
    cmp.w #$6ECA        ; list rows ($C2:6EC7)
    bne ++
    jsr list_slot
    bcc ++
    brl .out
++
    lda 6,s
    cmp.w #$20C4
    bne ++
    phy                 ; the FE/FF loop's string is at DB:($00): read the number ahead, the image needs only its own size
    ldy.w #$0001
    lda ($00),y
    ply
    jsr need
    lda 9,s
    cmp.w #$B70C
    beq .rank
    cmp.w #$C0CD
    bne ++
    lda 12,s
    cmp.w #$BF54        ; status page gear list ($C2:BF52 -> $C2:C0BD; its spell list from $C2:BF8C follows on from HEAD)
    bne ++
    lda.b $00
    cmp.w #$1236        ; its first name: the page packs up from the ring's bottom. From HEAD, the 3rd gear wrapped past the
    bne ++              ; panels onto the 1st ("Bronze Sword" -> "dronze Sword"), and the spells onto the gear
    sep #$20
    lda.b #!POOL
    sta.l !CFIRST
    rep #$20
++
    brl .other
+
    lda 9,s
    cmp.w #$B0F7
    beq .hud
    ; the wrapper's other callers leave the F0 at $0000,y (LDA $0001,y / INY: status pages $C2:B5FA, $C1:049E) or at ($02),y + 1
    ; ($C2:ABE4): read the number ahead too, so the image needs only its own size of free tiles
    cmp.w #$B5FD
    beq .y1
    cmp.w #$04A1
    beq .y1
    cmp.w #$ABE7
    beq +
    brl .other
+
    phy
    iny
    lda ($02),y
    ply
    bra .ahead
.y1:
    lda.w $0001,y
.ahead:
    jsr need
    brl .other
; rank panel names ($C2:B709 -> FE/FF loop, string at DB:($00)): drawn when the panel opens and kept beside the status page, whose
; description lines walked the lines ring over them (player bug report: "Gan" -> "kes!"). A panel name keyed by its far number | $8000.
.rank:
    sep #$20
    lda.b #$01
    sta.l !HUDC
    rep #$20
    phy
    ldy.w #$0001
    lda ($00),y         ; D and DB still the loop's
    ply
    pha
    ora.w #$8000
    sta.l !PKEY
    pla
    sec
    jsr drop_kind
    bra .num
.hud:
    sep #$20
    lda.b #$01
    sta.l !HUDC
    rep #$20
    lda.b $00           ; D is still the panel routine's
    and.w #$00F0
    sta.l !PKEY
    lda.w $0002,y       ; the far number, DB:Y as the caller left them
    clc
    jsr drop_kind
.num:
    jsr need
    ldx.w #(!CACHEN-1)*4
.find:
    cmp.l !CACHE,x
    beq .hit
.next:
    dex
    dex
    dex
    dex
    bpl .find
    sep #$20            ; a new HUD name: packed down from the ring's top, off the other panels' names
    jsr hud_place
    sta.l !CFIRST
    bra .out
.hit:
    pha
    lda.l !CACHE+2,x
    and.w #$00FF
    cmp.w #!POOL        ; 0: dropped (or WRAM zeroed by a block load)
    bcc .miss
    cmp.w #!POOLB
    bcs .miss
    sep #$20
    sta.l !CFIRST
    sta.l !HIT
    jsr use_slot
    rep #$20
    pla
.out:
    sep #$20
    lda.l !CFIRST
    rep #$10
    plx
    plp
    rts
.miss:
    pla
    bra .next
.other:
    sep #$20
    lda.l !CFIRST
    jsr protect
    sta.l !CFIRST
    bra .out

; Drop the other kind's panel entries: the rank panel and the HUD panels never share a screen, and a stale entry kept its ring
; tiles off the next screen's names. C set (a rank name): drop keys < $8000 (HUD); C clear: drop keys >= $8000 (rank). A16 X16, A X kept.
drop_kind:
    pha
    phx
    php
    ldx.w #(!PANELN-1)*4
-
    plp
    php
    lda.l !PANEL,x
    bcs .rank
    bpl .keep
    bra .drop
.rank:
    bmi .keep
.drop:
    sep #$20
    lda.b #$00
    sta.l !PANEL+2,x
    rep #$20
.keep:
    dex
    dex
    dex
    dex
    bpl -
    plp
    plx
    pla
    rts

; $C2:2726, the boot load of block 4 (A = 4). Block 4 is built without its 512 zero bytes (repack.TRIM) so the mid-game load
; ($C2:2706) no longer wipes our state at $7F:FE00-FFFF; at boot those zeros were its init (name entry showed junk without them).
boot_block4:
    jsl $828024
    php
    rep #$30
    pha
    phx
    ldx.w #$01FE
-
    lda.w #$0000
    sta.l $7FFE00,x
    dex
    dex
    bpl -
    plx
    pla
    plp
    rtl

; List rows ($C2:6EC7, 8 cells a row: shop and item lists, up to 5 rows on screen): a row's name goes into its own 8 tiles from !POOL
; up, picked by the row's tilemap address ($11EF), so a page flip redraws each row over itself. Was the ring: 5 names of up to 8 plus
; the panels' names didn't fit, it wrapped and a row went over another (player bug report: shop names wrong after left/right page flips,
; "Wooden Shield" -> "or den Shield"). Rows are $40 or $60 words apart: (address / $20) mod 5 differs for any 5 rows in a row unless
; the step is a multiple of 5. Panels pack down from !POOLB (hud_place); a panel entry under the slot is dropped, so it redraws into new
; tiles. A16 X16 in, DB:($0E),Y = the F0. C set: CFIRST = the slot; C clear: image over 8 tiles, the ring as before.
list_slot:
    phy
    iny
    lda ($0E),y
    ply
    jsr need
    sep #$20
    lda.l !NEED
    cmp.b #9
    rep #$20
    bcs .no
    lda.l $7E11EF
    lsr
    lsr
    lsr
    lsr
    lsr
    sta.l $004204       ; hardware divider: 16 / 8 bits, 16 cycles
    sep #$20
    lda.b #5
    sta.l $004206
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lda.l $004216       ; remainder
    asl
    asl
    asl
    clc
    adc.b #!POOL
    sta.l !CFIRST
    ldx.w #(!PANELN-1)*4
.drop:
    jsr protect_meets
    bcc +
    lda.b #$00
    sta.l !PANEL+2,x
+
    dex
    dex
    dex
    dex
    bpl .drop
    rep #$20
    sec
    rts
.no:
    clc
    rts

; A16 = far number -> !NEED = its image's tile count (stays !ROOM if out of range). A, X, Y kept.
need:
    pha
    phx
    asl
    asl
    tax
    lda.l !IMAGES+3,x
    and.w #$00FF
    beq +
    cmp.w #!ROOM+1
    bcs +
    sep #$20
    sta.l !NEED
    rep #$20
+
    plx
    pla
    rts

; -> A8 = the first tile for a new HUD name of !NEED tiles: as high in the names ring as it fits below the panels' names, so they
; stay together at the top and the other images get one gap from !POOL up instead of the holes between them (player bug report:
; 5 panel names spread over the ring left no 10-tile gap, and a Magic page went over them). No fit: protect from HEAD. X, Y kept.
hud_place:
    phx
    phy
    lda.b #!POOLB
    sec
    sbc.l !NEED
    sta.l !CFIRST
    ldy.w #!PANELN+1
.pass:
    lda.b #$00
    sta.l !MOVED
    ldx.w #(!PANELN-1)*4
.each:
    jsr protect_meets
    bcc +
    lda.l !PANEL+2,x    ; below it
    sec
    sbc.l !NEED
    cmp.b #!POOL
    bcc .full
    sta.l !CFIRST
    sta.l !MOVED
+
    dex
    dex
    dex
    dex
    bpl .each
    lda.l !MOVED
    beq .done
    dey
    bne .pass
.full:
    lda.l !HEAD
    jsr protect
    sta.l !CFIRST
.done:
    lda.l !CFIRST
    ply
    plx
    rts

; X16 = cache slot x 4 of a HUD name just drawn: panel !PKEY now shows it, so the name it showed before is free. A new key takes the
; next entry in turn. A8 out, X kept.
use_slot:
    phx
    rep #$20
    lda.l !CACHE+2,x    ; first tile, count
    pha
    lda.l !PKEY
    ldx.w #(!PANELN-1)*4
.find:
    cmp.l !PANEL,x
    beq .set
    dex
    dex
    dex
    dex
    bpl .find
    sep #$20
    lda.l !PROT
    clc
    adc.b #4
    and.b #$1C          ; WRAM at boot holds anything
    cmp.b #!PANELN*4
    bcc +
    lda.b #$00
+
    sta.l !PROT
    rep #$20
    and.w #$00FF
    tax
    lda.l !PKEY
.set:
    sta.l !PANEL,x
    pla
    sta.l !PANEL+2,x
    sep #$20
    plx
    rts

; A8 = a names-ring image's first tile -> A8 past every name a HUD panel shows. The panels draw a name once and keep it on screen
; while a status box flips pages, and each page's gear / spell names took new ring tiles over it (player bug reports: "Rick" ->
; "rWoo"; with 5 panels, Kojiro -> "Bronze" when only the two names used last were kept). Passes until none moves the start; still
; moving after PANELN + 1 passes = no room: the old start, over them as before. X, Y kept.
protect:
    phx
    phy
    sta.l !CFIRST
    pha
    ldy.w #!PANELN+1
.pass:
    lda.b #$00
    sta.l !MOVED
    ldx.w #(!PANELN-1)*4
.each:
    jsr .one
    bcc +
    sta.l !MOVED        ; the new start, nonzero
+
    dex
    dex
    dex
    dex
    bpl .each
    lda.l !MOVED
    beq .done
    dey
    bne .pass
    pla
    sta.l !CFIRST
    bra .out
.done:
    pla
.out:
    lda.l !CFIRST
    ply
    plx
    rts
; X16 = panel entry x 4: C set if [CFIRST, CFIRST + NEED) meets its image, CFIRST moved past it (to POOL if the image would not
; fit below POOLB there)
.one:
    jsr protect_meets
    bcc .no
    lda.l !PANEL+2,x
    clc
    adc.l !PANEL+3,x
    pha
    clc
    adc.l !NEED
    cmp.b #!POOLB+1
    pla
    bcc +
    lda.b #!POOL
+
    sta.l !CFIRST
    sec
    rts
.no:
    clc
    rts

; X16 = panel entry x 4: C set if [CFIRST, CFIRST + NEED) meets its image. A8 clobbered.
protect_meets:
    lda.l !PANEL+2,x
    cmp.b #!POOL
    bcc .no             ; 0: none
    cmp.b #!POOLB
    bcs .no
    lda.l !CFIRST
    clc
    adc.l !NEED
    cmp.l !PANEL+2,x
    beq .no
    bcc .no             ; ends before it
    lda.l !PANEL+2,x
    clc
    adc.l !PANEL+3,x
    cmp.l !CFIRST
    beq .no
    bcc .no             ; starts after it
    sec
    rts
.no:
    clc
    rts

; A8 = the image's end tile, from small_load (names ring). A hit: the head stays. A miss: the head moves there, cached images under
; the new one are dropped, and this one is cached. X, Y kept.
cache_put:
    pha
    lda.l !HIT
    beq +
    pla
    rts
+
    pla
    sta.l !CEND
    lda.l !HUDC
    bne +               ; a HUD name went in at the top (hud_place): the other images' ring head stays
    lda.l !CEND
    sta.l !HEAD
+
    phx
    lda.l !NEXT
    dec
    dec
    sta.l !CFIRST
    ldx.w #(!CACHEN-1)*4
.drop:
    lda.l !CACHE+2,x
    cmp.l !CEND
    bcs .keep           ; starts at or after the new image's end
    clc
    adc.l !CACHE+3,x    ; its end (pool tiles < $A0 and counts <= !ROOM: no carry)
    cmp.l !CFIRST
    beq .keep
    bcc .keep           ; ends at or before the new image's start
    lda.b #$00
    sta.l !CACHE+2,x
.keep:
    dex
    dex
    dex
    dex
    bpl .drop
    lda.l !HUDC
    beq .done           ; only HUD names are looked up (name_cache): no slot for the rest
    lda.l !CROT
    clc
    adc.b #4
    and.b #$1C          ; WRAM at boot holds anything
    cmp.b #!CACHEN*4
    bcc +
    lda.b #$00
+
    sta.l !CROT
    rep #$20
    and.w #$00FF
    tax
    lda.l !NUM
    sta.l !CACHE,x
    sep #$20
    lda.l !CFIRST
    sta.l !CACHE+2,x
    lda.l !CEND
    sec
    sbc.l !CFIRST
    sta.l !CACHE+3,x
    jsr use_slot
.done:
    plx
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

; VS-mode date "0年目 4月" ($C2:A7E7 built it in $1236 for $C2:140A): English "Year 0, April" (4月 is the calendar month).
; Up to 26 bytes with the centring pads (.centre): runs into $1246, the item-description scratch slot, free while this box shows.
; A = rank from $82:AE26. HUD bar row 2 (rect $1111, 30x2): cells 12-15 = N o . digit, the V sign follows at 16. DB as the caller's.
rank_text:
    inc a
    xba
    ora.w #$002A        ; the ・ tile, a stop (font.SMALL_DOT)
    sta.w $113F
    lda.w #$3E18
    sta.w $113D
    rtl

date_text:
    ldy.w #$1236
    ldx.w #.year-.s
    jsr .put
    lda.w $0A2D
    and.w #$00FF
    jsr .num
    ldx.w #.comma-.s
    jsr .put
    lda.w $0A2E         ; month as the original: (n + 3) mod 12, 1-12
    and.w #$00FF
    clc
    adc.w #3
    cmp.w #13
    bcc +
    sbc.w #12
+   dec
    asl
    tax
    lda.l .months,x
    tax
    jsr .put
    jsr .centre
    lda.w #$FFFF
    sta.w $0000,y
    rtl
.centre:                ; Y = end. Lead with (109 - px) / 8 spaces (4 px): the box's text area is 105 px from the first pen
    phy                 ; position (measured, tour vs), so this centres it. Capped at 24 bytes + FFFF ($1236-$124F; the $1246
                        ; slot takes 33-byte JP item descriptions). Longest real need: "Year 99, September" + 1 pad = 19.
    lda.w #109
    pha                 ; 1,s = 109 - px so far, 3,s = end
    ldx.w #$1236
.sum:
    txa
    cmp 3,s
    bcs .sumd
    lda.w $0000,x
    and.w #$00FF
    sec
    sbc.w #$000A        ; width is indexed from the first glyph code
    phx
    tax
    lda.l width,x
    plx
    and.w #$00FF
    eor.w #$FFFF
    inc
    clc
    adc 1,s
    sta 1,s
    inx
    bra .sum
.sumd:
    pla
    bmi .none
    lsr
    lsr
    lsr
    pha                 ; 1,s = pads, 3,s = end
    lda.w #$1236+24
    sec
    sbc 3,s             ; room left in 24 bytes
    bmi .none2
    cmp 1,s
    bcs +
    sta 1,s
+   lda 3,s
    dec
    tax                 ; last byte
    pla
    beq .none
    clc
    adc 1,s
    sta 1,s             ; new end, returned in Y
    dec
    tay
    sep #$20
.cp:
    lda.w $0000,x
    sta.w $0000,y
    dey
    dex
    cpx.w #$1236-1
    bne .cp
    lda.b #$3E          ; space
.fill:
    sta.w $0000,y
    dey
    cpy.w #$1236-1
    bne .fill
    rep #$20
    ply
    rts
.none2:
    pla
.none:
    ply
    rts
.num:                   ; A = 0-99 -> narrow ASCII digits ('0' = $60), no leading zero
    sta.w $4204
    sep #$20
    lda.b #10
    sta.w $4206
    nop #8
    lda.w $4214
    beq +
    clc
    adc.b #$60
    sta.w $0000,y
    iny
+   lda.w $4216
    clc
    adc.b #$60
    sta.w $0000,y
    iny
    rep #$20
    rts
.put:                   ; copy .s+X until 00 to Y
    sep #$20
-   lda.l .s,x
    beq +
    sta.w $0000,y
    inx
    iny
    bra -
+   rep #$20
    rts
.months:
    dw .jan-.s, .feb-.s, .mar-.s, .apr-.s, .may-.s, .jun-.s, .jul-.s, .aug-.s, .sep-.s, .oct-.s, .nov-.s, .dec-.s
.s:                     ; en.tbl codes: A-Z $0A, a-z $24, space $3E, comma $4A
.year:  db $22,$28,$24,$35,$3E,0                    ; "Year "
.comma: db $4A,$3E,0                                ; ", "
.jan:   db $13,$24,$31,$38,$24,$35,$3C,0            ; January
.feb:   db $0F,$28,$25,$35,$38,$24,$35,$3C,0        ; February
.mar:   db $16,$24,$35,$26,$2B,0                    ; March
.apr:   db $0A,$33,$35,$2C,$2F,0                    ; April
.may:   db $16,$24,$3C,0                            ; May
.jun:   db $13,$38,$31,$28,0                        ; June
.jul:   db $13,$38,$2F,$3C,0                        ; July
.aug:   db $0A,$38,$2A,$38,$36,$37,0                ; August
.sep:   db $1C,$28,$33,$37,$28,$30,$25,$28,$35,0    ; September
.oct:   db $18,$26,$37,$32,$25,$28,$35,0            ; October
.nov:   db $17,$32,$39,$28,$30,$25,$28,$35,0        ; November
.dec:   db $0D,$28,$26,$28,$30,$25,$28,$35,0        ; December

planebit:
    db 1, 2, 4, 8
tilecol:
    dw 0, 32, 128, 160
width:
    incbin "../build/vwf_width.bin"
font:
    incbin "../build/vwf_font.bin"
assert pc() <= $E08000
