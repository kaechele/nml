__license__ = """
NML is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

NML is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with NML; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

# -*- coding: utf-8 -*-
import codecs
from nml import generic, grfstrings, output_base

class OutputNFO(output_base.BinaryOutputBase):
    def __init__(self, filename, start_sprite_num):
        output_base.BinaryOutputBase.__init__(self, filename)
        self.sprite_num = start_sprite_num

    def open_file(self):
        handle = codecs.open(self.filename, 'w', 'utf-8')
        handle.write('// Automatically generated by GRFCODEC. Do not modify!\n'
                     '// (Info version 32)\n'
                     '// Escapes: 2+ 2- 2< 2> 2u< 2u> 2/ 2% 2u/ 2u% 2* 2& 2| 2^ 2sto = 2s 2rst = 2r 2psto 2ror = 2rot 2cmp 2ucmp 2<< 2u>> 2>>\n'
                     '// Escapes: 71 70 7= 7! 7< 7> 7G 7g 7gG 7GG 7gg 7c 7C\n'
                     '// Escapes: D= = DR D+ = DF D- = DC Du* = DM D* = DnF Du<< = DnC D<< = DO D& D| Du/ D/ Du% D%\n'
                     '// Format: spritenum imagefile depth xpos ypos xsize ysize xrel yrel zoom flags\n\n')
        return handle

    def print_byte(self, value):
        value = self.prepare_byte(value)
        self.file.write("\\b" + str(value) + " ")

    def print_bytex(self, value, pretty_print = None):
        value = self.prepare_byte(value)
        if pretty_print is not None:
            self.file.write(pretty_print + " ")
            return
        self.file.write("%02X " % value)

    def print_word(self, value):
        value = self.prepare_word(value)
        self.file.write("\\w%d " % value)

    def print_wordx(self, value):
        value = self.prepare_word(value)
        self.file.write("\\wx%04X " % value)

    def print_dword(self, value):
        value = self.prepare_dword(value)
        self.file.write("\\d%d " % value)

    def print_dwordx(self, value):
        value = self.prepare_dword(value)
        self.file.write("\\dx%08X " % value)

    def print_string(self, value, final_zero = True, force_ascii = False):
        assert self._in_sprite
        self.file.write('"')
        if not grfstrings.is_ascii_string(value):
            if force_ascii:
                raise generic.ScriptError("Expected ascii string but got a unicode string")
            self.file.write('\xC3\x9E'.decode('utf-8'))
        self.file.write(value.replace('"', '\\"'))
        self._byte_count += grfstrings.get_string_size(value, final_zero, force_ascii)
        self.file.write('" ')
        if final_zero:
            self.print_bytex(0)
            # get_string_size already includes the final 0 byte
            # but print_bytex also increases _byte_count, so decrease
            # it here by one to correct it.
            self._byte_count -= 1

    def print_decimal(self, value):
        assert self._in_sprite
        self.file.write(str(value) + " ")

    def newline(self, msg = "", prefix = "\t"):
        if msg != "": msg = prefix + "// " + msg
        self.file.write(msg + "\n")


    def comment(self, msg):
        self.file.write("// " + msg + "\n")

    def start_sprite(self, size, is_real_sprite = False):
        output_base.BinaryOutputBase.start_sprite(self, size)
        self.print_decimal(self.sprite_num)
        self.sprite_num += 1
        if not is_real_sprite:
            self.file.write("* ")
            self.print_decimal(size)

    def print_sprite(self, sprite_list):
        """
        @param sprite_list: List of non-empty real sprites for various bit depths / zoom levels
        @type sprite_list: C{list} of L{RealSprite}
        """
        self.start_sprite(0, True)
        for i, sprite_info in enumerate(sprite_list):
            self.file.write(sprite_info.file.value + " ")
            self.file.write("8bpp ")
            self.print_decimal(sprite_info.xpos.value)
            self.print_decimal(sprite_info.ypos.value)
            self.print_decimal(sprite_info.xsize.value)
            self.print_decimal(sprite_info.ysize.value)
            self.print_decimal(sprite_info.xrel.value)
            self.print_decimal(sprite_info.yrel.value)
            self.file.write("normal ")
            if (sprite_info.compression.value & 0x40) != 0:
                self.file.write("nocrop ")
            if i + 1 < len(sprite_list):
                self.newline()
                self.file.write("|\t")
        self.end_sprite()

    def print_empty_realsprite(self):
        self.start_sprite(1)
        self.print_bytex(0)
        self.end_sprite()

    def print_named_filedata(self, filename):
        self.start_sprite(0, True)
        self.file.write("** " + filename)
        self.end_sprite()
