Collector for the BIND. Collector parses XML Statistics in version 3

This collector is similar to that you can find in Diamond repository. 
However collector in diamond currently support BIND XML in version 2
python-diamond/Diamond



#### Dependencies
 * [bind 9.10]
    configured with libxml2 and statistics-channels
    More info: 
    https://kb.isc.org/article/AA-00769/0/Using-BINDs-XML-statistics-channels.html   
 
#### Requirements
 * You need enable statistics channel in a named instance
   statistics-channels {
   inet 127.0.0.1  port 8053 allow { any; };
   };


 * You can enable zone statistics globally or per zone basis
   eg. zone "example" {  zone-statistics yes; };

