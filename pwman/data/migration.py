# ============================================================================
# This file is part of Pwman3.
#
# Pwman3 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2
# as published by the Free Software Foundation;
#
# Pwman3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pwman3; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ============================================================================
# Copyright (C) 2021 Oz N Tiram <oz.tiram@gmail.com>
# ============================================================================



class MigrateZeroSixToZeroSeven:

    """
    Migrate from 0.6 to 0.7

    Add column MDATE to the Nodes.
    """

    def __init__(self):
        pass
    
    def apply(self):

        print("Will Apply some SQL magic")

migrations = {"0.7": (MigrateZeroSixToZeroSeven,)}
