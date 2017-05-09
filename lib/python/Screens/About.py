from Screen import Screen
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Harddisk import harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Tools.StbHardware import getFPVersion
from enigma import eTimer, eLabel, eConsoleAppContainer
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
import skin, os

class About(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_('About'))
        hddsplit, = skin.parameters.get('AboutHddSplit', (0,))
        bhVer = 'Black Hole'
        f = open('/etc/imageversion', 'r')
        bhVer = f.readline().strip()
        f.close()

        bhRev = ''
        f = open('/etc/bhrev', 'r')
        bhRev = f.readline().strip()
        f.close()

        driverdate = self.getDriverInstalledDate()
        if driverdate == 'unknown':
            driverdate = self.getDriverInstalledDate_proxy()

        self['DriverVersion'] = StaticText(_('DVB drivers: ') + driverdate)
        self['KernelVersion'] = StaticText(_('Kernel version: ') + self.getKernelVersionString())
        self['FPVersion'] = StaticText('Support: SODO sssd45@gmail.com')
        self['CpuInfo'] = StaticText(_('CPU: ') + self.getCPUInfoString())
        
        AboutText = _('Black Hole ') + bhVer + '\n'
        AboutText += _('Support: SODO sssd45@gmail.com') + '\n\n'

        AboutText += _('Hardware: ') + about.getHardwareTypeString() + '\n'
        AboutText += _('CPU: ') + about.getCPUInfoString() + '\n'
        AboutText += _('Installed: ') + about.getFlashDateString() + '\n'
        AboutText += _('Kernel version: ') + about.getKernelVersionString() + '\n'

        self["EnigmaVersion"] = StaticText("Enigma: " + about.getEnigmaVersionString())
        self["ImageVersion"] = StaticText("Firmware: " + bhVer + " " + bhRev)
        AboutText += _('Enigma (re)starts: %d\n') % config.misc.startCounter.value

        GStreamerVersion = 'GStreamer: ' + about.getGStreamerVersionString().replace('GStreamer', '')
        self['GStreamerVersion'] = StaticText(GStreamerVersion)
        AboutText += GStreamerVersion + '\n'

        AboutText += _('DVB drivers: ') + about.getDriverInstalledDate() + '\n'

        AboutText += _("Python version: ") + about.getPythonVersionString() + "\n"

        fp_version = getFPVersion()
        if fp_version is None:
            fp_version = ""
        else:
            fp_version = _("Frontprocessor version: %s") % fp_version
            AboutText += fp_version + "\n"

        self["FPVersion"] = StaticText(fp_version)

        self['TunerHeader'] = StaticText(_('Detected NIMs:'))
        AboutText += '\n' + _('Detected NIMs:') + '\n'

        nims = nimmanager.nimList(showFBCTuners=False)
        for count in range(len(nims)):
            if count < 4:
                self['Tuner' + str(count)] = StaticText(nims[count])
            else:
                self['Tuner' + str(count)] = StaticText('')
            AboutText += nims[count] + '\n'

        self['HDDHeader'] = StaticText(_('Detected HDD:'))
        AboutText += '\n' + _('Detected HDD:') + '\n'
        hddlist = harddiskmanager.HDDList()
        hddinfo = ''
        if hddlist:
            formatstring = hddsplit and '%s:%s, %.1f %sB %s' or '%s\n(%s, %.1f %sB %s)'
            for count in range(len(hddlist)):
                if hddinfo:
                    hddinfo += '\n'
                hdd = hddlist[count][1]
                if int(hdd.free()) > 1024:
                    hddinfo += formatstring % (hdd.model(),
                     hdd.capacity(),
                     hdd.free() / 1024.0,
                     'G',
                     _('free'))
                else:
                    hddinfo += formatstring % (hdd.model(),
                     hdd.capacity(),
                     hdd.free(),
                     'M',
                     _('free'))

        else:
            hddinfo = _('none')
        self['hddA'] = StaticText(hddinfo)
        AboutText += hddinfo + "\n\n" + _("Network Info:")
        for x in about.GetIPsFromNetworkInterfaces():
                 AboutText += "\n" + x[0] + ": " + x[1]

        self['AboutScrollLabel'] = ScrollLabel(AboutText)
        self['key_green'] = Button(_('Translations'))
        self['key_red'] = Button(_('Latest Commits'))
        self['key_yellow'] = Button(_("Troubleshoot"))
        self['key_blue'] = Button(_('Memory Info'))
        self['actions'] = ActionMap(['ColorActions', 'SetupActions', 'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'red': self.showCommits,
         'green': self.showTranslationInfo,
         'blue': self.showMemoryInfo,
         'yellow': self.showTroubleshoot,
         'up': self['AboutScrollLabel'].pageUp,
         'down': self['AboutScrollLabel'].pageDown})

    def getCPUInfoString(self):
        try:
            cpu_count = 0
            for line in open('/proc/cpuinfo').readlines():
                line = [ x.strip() for x in line.strip().split(':') ]
                if line[0] == 'system type':
                    processor = line[1].split()[0]
                if line[0] == 'cpu MHz':
                    cpu_speed = '%1.0f' % float(line[1])
                    cpu_count += 1

            return '%s %s MHz %d cores' % (processor, cpu_speed, cpu_count)
        except:
            return _('undefined')

    def getDriverInstalledDate(self):
        try:
            driver = os.popen('opkg list-installed | grep vuplus-dvb-modules').read().strip()
            driver = driver.split('-')
            return driver[5]
        except:
            return 'unknown'

    def getDriverInstalledDate_proxy(self):
        try:
            driver = os.popen('opkg list-installed | grep vuplus-dvb-proxy').read().strip()
            driver = driver.split('-')
            driver = driver[4].split('.')
            return driver[0]
        except:
            return _('unknown')

    def getKernelVersionString(self):
        try:
            return open('/proc/version', 'r').read().split(' ', 4)[2].split('-', 2)[0]
        except:
            return _('unknown')

    def showTranslationInfo(self):
        self.session.open(TranslationInfo)

    def showCommits(self):
        self.session.open(CommitInfo)

    def showMemoryInfo(self):
        self.session.open(MemoryInfo)
        
    def showTroubleshoot(self):
        self.session.open(Troubleshoot)
        
class TranslationInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        info = _('TRANSLATOR_INFO')
        if info == 'TRANSLATOR_INFO':
            info = '(N/A)'
        infolines = _('').split('\n')
        infomap = {}
        for x in infolines:
            l = x.split(': ')
            if len(l) != 2:
                continue
            type, value = l
            infomap[type] = value

        print infomap
        self['key_red'] = Button(_('Cancel'))
        self['TranslationInfo'] = StaticText(info)
        translator_name = infomap.get('Language-Team', 'none')
        if translator_name == 'none':
            translator_name = infomap.get('Last-Translator', '')
        self['TranslatorName'] = StaticText(translator_name)
        self['actions'] = ActionMap(['SetupActions'], {'cancel': self.close,
         'ok': self.close})


class CommitInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = ['CommitInfo', 'About']
        self['AboutScrollLabel'] = ScrollLabel(_('Please wait'))
        self['actions'] = ActionMap(['SetupActions', 'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'up': self['AboutScrollLabel'].pageUp,
         'down': self['AboutScrollLabel'].pageDown,
         'left': self.left,
         'right': self.right})
        self['key_red'] = Button(_('Cancel'))
        self.project = 0
        self.projects = [('enigma2', 'Enigma2'),
         ('Black Hole', 'Depend on Openpli Oe Core'),
         ('enigma2-plugins', 'Enigma2 Plugins'),
         ('aio-grab', 'Aio Grab'),
         ('gst-plugin-dvbmediasink', 'Gst Plugin Dvbmediasink'),
         ('HenksatSettings', 'Henksat Settings'),
         ('enigma2-plugin-extensions-xmltvimport', 'Plugin Xmltvimport'),
         ('enigma2-plugin-skins-magic', 'Skin Magic SD'),
         ('tuxtxt', 'Tuxtxt')]
        self.cachedProjects = {}
        self.Timer = eTimer()
        self.Timer.callback.append(self.readGithubCommitLogs)
        self.Timer.start(50, True)

    def readGithubCommitLogs(self):
        url = 'https://api.github.com/repos/openpli2/%s/commits' % self.projects[self.project][0]
        commitlog = ''
        from datetime import datetime
        from json import loads
        from urllib2 import urlopen
        try:
            commitlog += 80 * '-' + '\n'
            commitlog += url.split('/')[-2] + '\n'
            commitlog += 80 * '-' + '\n'
            for c in loads(urlopen(url, timeout=5).read()):
                creator = c['commit']['author']['name']
                title = c['commit']['message']
                date = datetime.strptime(c['commit']['committer']['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%x %X')
                commitlog += date + ' ' + creator + '\n' + title + '\n\n'

            commitlog = commitlog.encode('utf-8')
            self.cachedProjects[self.projects[self.project][1]] = commitlog
        except:
            commitlog += _('You are using Black Hole Image To vuplus' '\n\n' 'Build By REDOUANE' '\n\n' 'Supported' '\n'
'sss54@gmail.com' '\n\n' 'Enjoy')

        self['AboutScrollLabel'].setText(commitlog)

    def updateCommitLogs(self):
        if self.cachedProjects.has_key(self.projects[self.project][1]):
            self['AboutScrollLabel'].setText(self.cachedProjects[self.projects[self.project][1]])
        else:
            self['AboutScrollLabel'].setText(_('Please wait'))
            self.Timer.start(50, True)

    def left(self):
        self.project = self.project == 0 and len(self.projects) - 1 or self.project - 1
        self.updateCommitLogs()

    def right(self):
        self.project = self.project != len(self.projects) - 1 and self.project + 1 or 0
        self.updateCommitLogs()


class MemoryInfo(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'cancel': self.close,
         'ok': self.getMemoryInfo,
         'green': self.getMemoryInfo,
         'blue': self.clearMemory})
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Refresh'))
        self['key_blue'] = Label(_('Clear'))
        self['lmemtext'] = Label()
        self['lmemvalue'] = Label()
        self['rmemtext'] = Label()
        self['rmemvalue'] = Label()
        self['pfree'] = Label()
        self['pused'] = Label()
        self['slide'] = ProgressBar()
        self['slide'].setValue(100)
        self['params'] = MemoryInfoSkinParams()
        self['info'] = Label(_("This info is for developers only.\nFor a normal users it is not relevant.\nDon't panic please when you see values being displayed that you think look suspicious!"))
        self.setTitle(_('Memory Info'))
        self.onLayoutFinish.append(self.getMemoryInfo)

    def getMemoryInfo(self):
        try:
            ltext = rtext = ''
            lvalue = rvalue = ''
            mem = 1
            free = 0
            rows_in_column = self['params'].rows_in_column
            for i, line in enumerate(open('/proc/meminfo', 'r')):
                s = line.strip().split(None, 2)
                if len(s) == 3:
                    name, size, units = s
                elif len(s) == 2:
                    name, size = s
                    units = ''
                else:
                    continue
                if name.startswith('MemTotal'):
                    mem = int(size)
                if name.startswith('MemFree') or name.startswith('Buffers') or name.startswith('Cached'):
                    free += int(size)
                if i < rows_in_column:
                    ltext += ''.join((name, '\n'))
                    lvalue += ''.join((size,
                     ' ',
                     units,
                     '\n'))
                else:
                    rtext += ''.join((name, '\n'))
                    rvalue += ''.join((size,
                     ' ',
                     units,
                     '\n'))

            self['lmemtext'].setText(ltext)
            self['lmemvalue'].setText(lvalue)
            self['rmemtext'].setText(rtext)
            self['rmemvalue'].setText(rvalue)
            self['slide'].setValue(int(100.0 * (mem - free) / mem + 0.25))
            self['pfree'].setText('%.1f %s' % (100.0 * free / mem, '%'))
            self['pused'].setText('%.1f %s' % (100.0 * (mem - free) / mem, '%'))
        except Exception as e:
            print '[About] getMemoryInfo FAIL:', e

    def clearMemory(self):
        eConsoleAppContainer().execute('sync')
        open('/proc/sys/vm/drop_caches', 'w').write('3')
        self.getMemoryInfo()


class MemoryInfoSkinParams(HTMLComponent, GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.rows_in_column = 25

    def applySkin(self, desktop, screen):
        if self.skinAttributes is not None:
            attribs = []
            for attrib, value in self.skinAttributes:
                if attrib == 'rowsincolumn':
                    self.rows_in_column = int(value)

            self.skinAttributes = attribs
        return GUIComponent.applySkin(self, desktop, screen)

    GUI_WIDGET = eLabel

class Troubleshoot(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("Troubleshoot"))
        self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))
        self["key_red"] = Button()
        self["key_green"] = Button()

        self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
            {
                "cancel": self.close,
                "up": self["AboutScrollLabel"].pageUp,
                "down": self["AboutScrollLabel"].pageDown,
                "left": self.left,
                "right": self.right,
                "red": self.red,
                "green": self.green,
            })

        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.appClosed)
        self.container.dataAvail.append(self.dataAvail)
        self.commandIndex = 0
        self.updateOptions()
        self.onLayoutFinish.append(self.run_console)

    def left(self):
        self.commandIndex = (self.commandIndex - 1) % len(self.commands)
        self.updateKeys()
        self.run_console()

    def right(self):
        self.commandIndex = (self.commandIndex + 1) % len(self.commands)
        self.updateKeys()
        self.run_console()

    def red(self):
        if self.commandIndex >= self.numberOfCommands:
            self.session.openWithCallback(self.removeAllLogfiles, MessageBox, _("Do you want to remove all the crahs logfiles"), default=False)
        else:
            self.close()

    def green(self):
        if self.commandIndex >= self.numberOfCommands:
            try:
                os.remove(self.commands[self.commandIndex][4:])
            except:
                pass
            self.updateOptions()
        self.run_console()

    def removeAllLogfiles(self, answer):
        if answer:
            for fileName in self.getLogFilesList():
                try:
                    os.remove(fileName)
                except:
                    pass
            self.updateOptions()
            self.run_console()

    def appClosed(self, retval):
        if retval:
            self["AboutScrollLabel"].setText(_("Some error occured - Please try later"))

    def dataAvail(self, data):
        self["AboutScrollLabel"].appendText(data)

    def run_console(self):
        self["AboutScrollLabel"].setText("")
        self.setTitle("%s - %s" % (_("Troubleshoot"), self.titles[self.commandIndex]))
        command = self.commands[self.commandIndex]
        if command.startswith("cat "):
            try:
                self["AboutScrollLabel"].setText(open(command[4:], "r").read())
            except:
                self["AboutScrollLabel"].setText(_("Logfile does not exist anymore"))
        else:
            try:
                if self.container.execute(command):
                    raise Exception, "failed to execute: ", command
            except Exception, e:
                self["AboutScrollLabel"].setText("%s\n%s" % (_("Some error occured - Please try later"), e))

    def cancel(self):
        self.container.appClosed.remove(self.appClosed)
        self.container.dataAvail.remove(self.dataAvail)
        self.container = None
        self.close()

    def getLogFilesList(self):
        import glob
        home_root = "/home/root/enigma2_crash.log"
        tmp = "/tmp/enigma2_crash.log"
        return [x for x in sorted(glob.glob("/mnt/hdd/*.log"), key=lambda x: os.path.isfile(x) and os.path.getmtime(x))] + (os.path.isfile(home_root) and [home_root] or []) + (os.path.isfile(tmp) and [tmp] or [])

    def updateOptions(self):
        self.titles = ["dmesg", "ifconfig", "df", "top", "ps"]
        self.commands = ["dmesg", "ifconfig", "df -h", "top -n 1", "ps"]
        install_log = "/home/root/autoinstall.log"
        if os.path.isfile(install_log):
                self.titles.append("%s" % install_log)
                self.commands.append("cat %s" % install_log)
        self.numberOfCommands = len(self.commands)
        fileNames = self.getLogFilesList()
        if fileNames:
            totalNumberOfLogfiles = len(fileNames)
            logfileCounter = 1
            for fileName in reversed(fileNames):
                self.titles.append("logfile %s (%s/%s)" % (fileName, logfileCounter, totalNumberOfLogfiles))
                self.commands.append("cat %s" % (fileName))
                logfileCounter += 1
        self.commandIndex = min(len(self.commands) - 1, self.commandIndex)
        self.updateKeys()

    def updateKeys(self):
        self["key_red"].setText(_("Cancel") if self.commandIndex < self.numberOfCommands else _("Remove all logfiles"))
        self["key_green"].setText(_("Refresh") if self.commandIndex < self.numberOfCommands else _("Remove this logfile"))
