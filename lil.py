import string
import time
import cherrypy

from bitcoin.rpc import RawProxy
import hashlib


cherrypy.server.socket_host = '0.0.0.0'


class BlockChainExplr(object):
    def tran (self,hash=""):
	p = RawProxy()
        sum_out=0
        sum_in=0
        fee=0
        vin_all=""
        vout_all=""
        raw_tx = p.getrawtransaction(hash)
        decoded_tx = p.decoderawtransaction(raw_tx)
        for u in decoded_tx['vout']:
            vout=""
            val=0
            val=u['value']
            sum_out=sum_out+val
            ss=u['scriptPubKey']
            if 'addresses' in ss:
                 for a in ss['addresses']:
                     vout=vout+"<div>"+a+"</div>"
            vout_all="%s<div class='output_inside'><div class='address'>%s</div><div class='value'>%s BTC</div></div>" % (vout_all,vout,str(val))
        if 'coinbase' not in decoded_tx['vin'][0]:
            for b in decoded_tx['vin']:
                 ii=b['vout']
                 new=p.decoderawtransaction(p.getrawtransaction(b['txid']))
                 vin=""
                 val_in=0
                 sss=new['vout'][ii]['scriptPubKey']
                 val_in=new['vout'][ii]['value']
                 sum_in=sum_in+val_in
                 if 'addresses' in sss:
                     for c in sss['addresses']:
                         vin=vin+"<div>"+c+"</div>"
                 vin_all="%s<div class='input_inside'><div class='address'>%s</div><div class='value'>%s BTC</div></div>" % (vin_all,vin,str(val_in))
            if sum_in-sum_out>0:
                 fee=sum_in-sum_out
        else:
            vin_all="<div class='input_inside'>COINBASE</div>"
        return """<h4>Tranzakcija: %s</h4><div class='tx_inside'>
<div class='input'>
<h5>ieigos</h5>
%s
<div class='sum'>Suma: %s BTC</div>

</div>

<div class='output'>
<h5>iseigos</h5>
%s
<div class='sum'>Suma: %s BTC</div>
</div>
</div><div class='fee'>Mokestis: %s BTC</div>
""" % ( hash, vin_all,str(sum_in),vout_all,str(sum_out),str(fee) )
    @cherrypy.expose
    def search(self, search=""):
	if search.isdigit():
		raise cherrypy.HTTPRedirect("/block?height="+search)
	p = RawProxy()
	sum=""
	hit=0
	seconds=time.time()
	i=p.getblockcount()
	list=search.split()
        while (i>=0) and (time.time()-seconds<120) and (hit<30):
                block=p.getblock(p.getblockhash(i))
		if (all(se in str(block['hash']) for se in list) or all(se in str(block['tx']) for se in list)):
			hit=hit+1
			sum=sum+"<li><a href=block?height="+str(i)+">"+p.getblockhash(i)+"</a></li>"
		i=i-1
        return """
<html>
          <head>
<link rel="stylesheet" type="text/css" href="style.css"></head>
          <body>
<form method="get" action="search">
                <input type="text" name="search">
              <button type="submit">ieskoti</button>
            </form>

                <ul>
                        %s
                </ul>
          </body>
        </html>
""" % sum

    @cherrypy.expose
    def index(self):
	p = RawProxy()
	number=p.getblockcount()
	return """
<html>
          <head>
<link rel="stylesheet" type="text/css" href="style.css"></head>
          <body>
<div class="index">
		<h3>Visi blokai: %d</h3>
<p>Ieskokite bloku grandineje. Irasius skaiciu (0-%d imtinai), nukeliaujama tiesiai i to gylio bloka.</p>
<form method="get" action="search">
		<input type="text" name="search">
              <button type="submit">ieskoti</button>
            </form>
</div>
          </body>
        </html>
""" % ( number+1,number )
    


    @cherrypy.expose
    def block(self, height=8):
	p = RawProxy()
	blockhash = p.getblockhash(int(height))
	block=p.getblock(blockhash)
	prev="none"
	if 'previousblockhash' in block:
	    prev="<a href=block?height=%d>%s</a>" % (int(height)-1,block['previousblockhash'])
	tr=block['tx']
	transactions=""
	if int(height)>0:
	    for f in tr:
	        transactions=transactions+self.tran(f)
	else:
	    transactions="<h4>Tranzakcija: "+tr[0]+"</h4><div></div>"
	return """<html>
          <head>
<link rel="stylesheet" type="text/css" href="style.css"></head>
          <body>
		<h3>Bloko hash'as %s</h3>
		<ul>
		<li>Versija: %d</li>
		<li>Sudetingumas: %d</li>
		<li>Nonce: %s</li>
		<li>praeito bloko hash'as: %s</li>
		<li>merkle saknis %s</li>
		</ul>
                <div class='all_tx'>%s</div>

<form method="get" action="/">
              <button type="submit">atgal</button>
            </form>
          </body>
        </html>""" % (blockhash,block['version'],int(block['bits'],16),block['nonce'],prev,block['merkleroot'],transactions)

if __name__ == '__main__':
    cherrypy.quickstart(BlockChainExplr(),config={

        '/user006':
        { 'tools.staticdir.on':True,
          'tools.staticdir.dir': "/home/user006"
        },

        '/style.css':
        { 'tools.staticfile.on':True,
          'tools.staticfile.filename': "/home/user006/style.css"
        }
    })

