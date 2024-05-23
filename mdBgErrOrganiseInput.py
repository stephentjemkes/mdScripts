#!/usr/bin/env python
# -*- coding: utf-8 -*-



from maatdafpy.WrfDeterministicCycleModule import WrfDeterministicCycleClass

if __name__ == '__main__':

    """
    The bgerr code for the nmc method needs the wrf data in a specific order
    it expects a directory with dates (e.g. 2022060100) which represents the analysis time i.e. start time of a forecast
    bundel. in this directory there are then two forecasts one with a 12 hour step and the other with a 24 hour steo
    (e.g. 2022060112 and 2022060200).
    the parent directory could have a number of base times 12 hour separated (2022060100, 2022060112, 2022060200, ...).
    """

    description = "DESCRIPTION:\n"
    description += "This script prepares the input for the genbe script\n"
    static_background_project = WrfDeterministicCycleClass(valid_options=None,
                                                           description=description,
                                                           processing_type="bgOrganise")
    static_background_project.__organise_genbe_input__()

