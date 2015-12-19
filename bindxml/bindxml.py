
"""

Collector for BIND XML Statistics in version 3


#### Dependencies
 * [bind 9.10]
    configured with libxml2 and statistics-channels

#### Requirements
 * You need enable statistics channel in a named instance
   statistics-channels {
   inet 127.0.0.1  port 8053 allow { any; };
   };


 * You can enable zone statistics globally or per zone basis
   eg. zone "example" {  zone-statistics yes; };


"""



import diamond.collector

import sys
import urllib2

if sys.version_info >= (2, 5):
    import xml.etree.cElementTree as ElementTree
    ElementTree  # workaround for pyflakes issue #13
else:
    import cElementTree as ElementTree

#Controller time
from datetime import datetime




class BindxmlCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(BindxmlCollector, self).get_default_config_help()
        config_help.update({
            'host': "",
            'port': "",
            'publish': "Available stats: \n"
            + " - zones  \n"
            + " - counters  \n"
            + " - server \n"
            + " - summary \n",
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(BindxmlCollector, self).get_default_config()
        config.update({
            'host': 'localhost',
            'port': 8053,
            # Available stats:
            'publish': [
                'zones',
                'counters',
                'server',
                'summary',
            ],
        })
        return config


    def collect(self):
        
        try:
            req = urllib2.urlopen('http://%s:%d/' % (
                self.config['host'], int(self.config['port'])))

        except Exception, e:
            print('Couldnt connect to bind: %s', e)

        tree = ElementTree.parse(req)

        if not tree:
            raise ValueError("Corrupt XML file, no statistics found")

        root = tree.getroot()

        #self.log.error('Debug config params: %s', self.config)

        if 'zones' in self.config['publish']:
            metric_prefix = "zones"
            for view in root.findall('views/view'):
                if view.get('name')=='_default':
                    metric_prefix="view."+view.get('name')+"."+metric_prefix
                    nzones = len(view.findall('zones/zone'))
                    self.publish(metric_prefix+".total", str(nzones))
                    for zoneview in view.findall('zones/zone'):
                        zone_name=zoneview.get('name')
                        zone_name=zone_name.replace(".", "_")
                        for zonecntrs in zoneview.findall('counters'):
                            counter_prefix = zonecntrs.attrib['type']
                            for zonecnt  in zonecntrs.findall('counter'):
                                counter_name=zonecnt.get('name').lower()
                            
                                self.publish(metric_prefix+"."+zone_name+"."
                                         +counter_prefix+"."+counter_name,
                                          int(zonecnt.text) )

        if 'counters' in self.config['publish']:
            metric_prefix = "counters"
            for view in root.findall('views/view'):
                if view.get('name')=='_default':
                    metric_prefix="view."+view.get('name')+"."+metric_prefix
                    for cntrsview in view.findall('counters'):
                        counter_prefix = cntrsview.attrib['type']
                        for cntview in cntrsview.findall('counter'):
                            counter_name=cntview.get('name').lower()
                            self.publish(metric_prefix+"."+counter_prefix+"."
                                         +counter_name, int(cntview.text) )
                                

        if 'server' in self.config['publish']:
            metric_prefix = "server"
            for counter in root.findall('server/counters'):
                prefix=metric_prefix+".counters"
                ctype = counter.get('type')
                for i in counter:
                    name = str(i.get('name'))
                    metric=name.lower()
                    self.publish(prefix+'.'+ctype +'.'+metric, int(i.text))

        if 'summary' in self.config['publish']:
            metric_prefix = "summary"
            for counter in root.findall('memory/summary'):
                for summ in counter:
                    metric=str(summ.tag)
                    metric=metric.lower()
                    self.publish(metric_prefix+'.'+metric, int(summ.text))


