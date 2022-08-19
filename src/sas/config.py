""" Configuration class - stores configuration information for SasView

The Config class cannot be subclassed or dynamically modified,
this prevents the config from having fields that are unspecified in
the base class, and makes it so that all usages of fields can be
automatically tracked. This allows the configs to be much more
easily maintained.

Dev note: I have opted not to use frozen dataclasses at this time
because, as they currently work, the behaviour would make creating
different configs difficult.
"""

from config_meta import ConfigBase, ConfigMeta

import sas.sasview
import os
import time


class Config(ConfigBase, metaclass=ConfigMeta):

    def __init__(self):
        super().__init__()

        # Version of the application
        self.__appname__ = "SasView"
        self.__version__ = sas.sasview.__version__
        self.__build__ = sas.sasview.__build__
        self.__download_page__ = 'https://github.com/SasView/sasview/releases'
        self.__update_URL__ = 'https://www.sasview.org/latestversion.json'

        # Debug message flag
        self.__EVT_DEBUG__ = False

        # Flag for automated testing
        self.__TEST__ = False

        # Debug message should be written to a file?
        self.__EVT_DEBUG_2_FILE__ = False
        self.__EVT_DEBUG_FILENAME__ = "debug.log"

        # About box info
        self._do_aboutbox = True
        self._do_acknowledge = True
        self._do_tutorial = True
        self._acknowledgement_preamble = \
            '''To ensure the long term support and development of this software please''' + \
            ''' remember to:'''
        self._acknowledgement_preamble_bullet1 = \
            '''Acknowledge its use in your publications as :'''
        self._acknowledgement_preamble_bullet2 = \
            '''Reference SasView as:'''
        self._acknowledgement_preamble_bullet3 = \
            '''Reference the model you used if appropriate (see documentation for refs)'''
        self._acknowledgement_preamble_bullet4 = \
            '''Send us your reference for our records: developers@sasview.org'''
        self._acknowledgement_publications = \
            '''This work benefited from the use of the SasView application, originally developed under NSF Award DMR-0520547. SasView also contains code developed with funding from the EU Horizon 2020 programme under the SINE2020 project Grant No 654000.'''
        self._acknowledgement_citation = \
            '''M. Doucet et al. SasView Version 5.0'''

        self._acknowledgement = \
            '''This work was originally developed as part of the DANSE project funded by the US NSF under Award DMR-0520547,\n but is currently maintained by a collaboration between UTK, UMD, NIST, ORNL, ISIS, ESS, ILL, ANSTO, TU Delft, DLS, and the scattering community.\n\n SasView also contains code developed with funding from the EU Horizon 2020 programme under the SINE2020 project (Grant No 654000).\nA list of individual contributors can be found at: http://www.sasview.org/contact.html
            '''

        self._homepage = "https://www.sasview.org"
        self._download = self.__download_page__
        self._authors = []
        self._paper = "http://sourceforge.net/p/sasview/tickets/"
        self._license = "mailto:help@sasview.org"

        self.icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "images"))
        # logging.info("icon path: %s" % icon_path)
        self.media_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "media"))
        self.test_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test"))

        self._nist_logo = os.path.join(self.icon_path, "nist_logo.png")
        self._umd_logo = os.path.join(self.icon_path, "umd_logo.png")
        self._sns_logo = os.path.join(self.icon_path, "sns_logo.png")
        self._ornl_logo = os.path.join(self.icon_path, "ornl_logo.png")
        self._isis_logo = os.path.join(self.icon_path, "isis_logo.png")
        self._ess_logo = os.path.join(self.icon_path, "ess_logo.png")
        self._ill_logo = os.path.join(self.icon_path, "ill_logo.png")
        self._ansto_logo = os.path.join(self.icon_path, "ansto_logo.png")
        self._tudelft_logo = os.path.join(self.icon_path, "tudelft_logo.png")
        self._dls_logo = os.path.join(self.icon_path, "dls_logo.png")
        self._nsf_logo = os.path.join(self.icon_path, "nsf_logo.png")
        self._danse_logo = os.path.join(self.icon_path, "danse_logo.png")
        self._inst_logo = os.path.join(self.icon_path, "utlogo.gif")
        self._nist_url = "https://www.nist.gov/"
        self._umd_url = "https://www.umd.edu/"
        self._sns_url = "https://neutrons.ornl.gov/"
        self._ornl_url = "https://neutrons.ornl.gov/"
        self._nsf_url = "https://www.nsf.gov"
        self._isis_url = "https://www.isis.stfc.ac.uk/"
        self._ess_url = "https://europeanspallationsource.se/"
        self._ill_url = "https://www.ill.eu/"
        self._ansto_url = "https://www.ansto.gov.au/"
        self._tudelft_url = "https://www.tudelft.nl/en/faculty-of-applied-sciences/business/facilities/reactor-institute-delft"
        self._dls_url = "https://www.diamond.ac.uk/"
        self._danse_url = "https://www.its.caltech.edu/~matsci/btf/DANSE_web_page.html"
        self._inst_url = "https://www.utk.edu"
        self._corner_image = os.path.join(self.icon_path, "angles_flat.png")
        self._welcome_image = os.path.join(self.icon_path, "SVwelcome.png")
        self._copyright = "(c) 2009 - 2022, UTK, UMD, NIST, ORNL, ISIS, ESS, ILL, ANSTO, TU Delft and DLS"
        self.marketplace_url = "http://marketplace.sasview.org/"

        # edit the list of file state your plugin can read
        self.APPLICATION_WLIST = 'SasView files (*.svs)|*.svs'
        self.APPLICATION_STATE_EXTENSION = '.svs'
        self.GUIFRAME_WIDTH = 1150
        self.GUIFRAME_HEIGHT = 840
        self.PLUGIN_STATE_EXTENSIONS = ['.fitv', '.inv', '.prv', '.crf']
        self.PLUGINS_WLIST = ['Fitting files (*.fitv)|*.fitv',
                         'Invariant files (*.inv)|*.inv',
                         'P(r) files (*.prv)|*.prv',
                         'Corfunc files (*.crf)|*.crf']
        self.PLOPANEL_WIDTH = 415
        self.PLOPANEL_HEIGTH = 370
        self.DATAPANEL_WIDTH = 235
        self.DATAPANEL_HEIGHT = 700
        self.SPLASH_SCREEN_PATH = os.path.join(self.icon_path, "SVwelcome_mini.png")
        self.TUTORIAL_PATH = os.path.join(self.media_path, "Tutorial.pdf")
        # DEFAULT_STYLE = GUIFRAME.MULTIPLE_APPLICATIONS|GUIFRAME.MANAGER_ON\
        #                    |GUIFRAME.CALCULATOR_ON|GUIFRAME.TOOLBAR_ON
        self.DEFAULT_STYLE = 64

        self.SPLASH_SCREEN_WIDTH = 512
        self.SPLASH_SCREEN_HEIGHT = 366
        self.SS_MAX_DISPLAY_TIME = 2000
        self.WELCOME_PANEL_ON = True
        self.WELCOME_PANEL_SHOW = False
        self.CLEANUP_PLOT = False
        # OPEN and SAVE project menu
        self.OPEN_SAVE_PROJECT_MENU = True
        # VIEW MENU
        self.VIEW_MENU = True
        # EDIT MENU
        self.EDIT_MENU = True

        self.SetupIconFile_win = os.path.join(self.icon_path, "ball.ico")
        self.SetupIconFile_mac = os.path.join(self.icon_path, "ball.icns")
        self.DefaultGroupName = "."
        self.OutputBaseFilename = "setupSasView"

        self.FIXED_PANEL = True
        self.DATALOADER_SHOW = True
        self.CLEANUP_PLOT = False
        self.WELCOME_PANEL_SHOW = False
        # Show or hide toolbar at the start up
        self.TOOLBAR_SHOW = True
        # set a default perspective
        self.DEFAULT_PERSPECTIVE = 'None'

        # Time out for updating sasview
        self.UPDATE_TIMEOUT = 2

        # OpenCL option
        self.SAS_OPENCL = None

        #
        # Lock the class down
        #
        self._lock()

    def printEVT(self, message):
        if self.__EVT_DEBUG__:
            """
            :TODO - Need method doc string
            """
            print("%g:  %s" % (time.clock(), message))

            if self.__EVT_DEBUG_2_FILE__:
                out = open(self.__EVT_DEBUG_FILENAME__, 'a')
                out.write("%10g:  %s\n" % (time.clock(), message))
                out.close()






