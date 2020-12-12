#
#  Erk IRC Client
#  Copyright (C) 2019  Daniel Hetrick
#               _   _       _                         
#              | | (_)     | |                        
#   _ __  _   _| |_ _  ___ | |__                      
#  | '_ \| | | | __| |/ _ \| '_ \                     
#  | | | | |_| | |_| | (_) | |_) |                    
#  |_| |_|\__,_|\__| |\___/|_.__/ _                   
#  | |     | |    _/ |           | |                  
#  | | __ _| |__ |__/_  _ __ __ _| |_ ___  _ __ _   _ 
#  | |/ _` | '_ \ / _ \| '__/ _` | __/ _ \| '__| | | |
#  | | (_| | |_) | (_) | | | (_| | || (_) | |  | |_| |
#  |_|\__,_|_.__/ \___/|_|  \__,_|\__\___/|_|   \__, |
#                                                __/ |
#                                               |___/ 
#  https://github.com/nutjob-laboratories
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
import html
from itertools import combinations

from .files import *
from .objects import *
from .resources import *
from . import config

STYLES = get_text_format_settings()

IRC_00 = "#FFFFFF"
IRC_01 = "#000000"
IRC_02 = "#00007F"
IRC_03 = "#009300"
IRC_04 = "#FF0000"
IRC_05 = "#7F0000"
IRC_06 = "#9C009C"
IRC_07 = "#FC7F00"
IRC_08 = "#FFFF00"
IRC_09 = "#00FC00"
IRC_10 = "#009393"
IRC_11 = "#00FFFF"
IRC_12 = "#0000FC"
IRC_13 = "#FF00FF"
IRC_14 = "#7F7F7F"
IRC_15 = "#D2D2D2"

HORIZONTAL_RULE = f'''
<table width="100%" border="0">
	<tbody>
		<tr>
			<td style="background-image: url({HORIZONTAL_RULE_BACKGROUND}); background-repeat: repeat-x;">&nbsp;
			</td>
		</tr>
	</tbody>
</table>'''

DATE_MESSAGE_TEMPLATE = f'''
<table width="100%" border="0">
	<tbody>
		<tr>
			<td style="background-image: url({HORIZONTAL_RULE_BACKGROUND}); background-repeat: repeat-x;">&nbsp;
			</td>
			<td><center><small><b>!MESSAGE!</b></small></center></td>
			<td style="background-image: url({HORIZONTAL_RULE_BACKGROUND}); background-repeat: repeat-x;">&nbsp;
			</td>
		</tr>
	</tbody>
</table>'''

LIGHT_HORIZONTAL_RULE = f'''
<table width="100%" border="0">
	<tbody>
		<tr>
			<td style="background-image: url({LIGHT_HORIZONTAL_RULE_BACKGROUND}); background-repeat: repeat-x;">&nbsp;
			</td>
		</tr>
	</tbody>
</table>'''

LIGHT_DATE_MESSAGE_TEMPLATE = f'''
<table width="100%" border="0">
	<tbody>
		<tr>
			<td style="background-image: url({LIGHT_HORIZONTAL_RULE_BACKGROUND}); background-repeat: repeat-x;">&nbsp;
			</td>
			<td><center><small><b>!MESSAGE!</b></small></center></td>
			<td style="background-image: url({LIGHT_HORIZONTAL_RULE_BACKGROUND}); background-repeat: repeat-x;">&nbsp;
			</td>
		</tr>
	</tbody>
</table>'''

# HORIZONTAL_RULE = f'''
# <table width="100%" border="0">
# 	<tbody>
# 		<tr>
# 			<td style="background-image: url($SEP); background-repeat: repeat-x;">&nbsp;
# 			</td>
# 		</tr>
# 	</tbody>
# </table>'''

# DATE_MESSAGE_TEMPLATE = f'''
# <table width="100%" border="0">
# 	<tbody>
# 		<tr>
# 			<td style="background-image: url($SEP)); background-repeat: repeat-x;">&nbsp;
# 			</td>
# 			<td><center><small><b>!MESSAGE!</b></small></center></td>
# 			<td style="background-image: url($SEP)); background-repeat: repeat-x;">&nbsp;
# 			</td>
# 		</tr>
# 	</tbody>
# </table>'''

TIMESTAMP_TEMPLATE = """<td style="vertical-align:top; font-size:small; text-align:left;"><div style="!TIMESTAMP_STYLE!">[!TIME!]</div></td><td style="font-size:small;">&nbsp;</td>"""

MESSAGE_TEMPLATE = f"""
<table style="width: 100%;" border="0">
	<tbody>
	<tr>!TIMESTAMP!
		<td style="text-align: right; vertical-align: top;"><div style="!ID_STYLE!">!ID!</div></td>
		<td style="text-align: left; vertical-align: top;">&nbsp;</td>
		!INSERT_MESSAGE_TEMPLATE!
	</tr>
	</tbody>
</table>
"""

SYSTEM_TEMPLATE = f"""
<table style="width: 100%;" border="0">
	<tbody>
	<tr>!TIMESTAMP!
		!INSERT_MESSAGE_TEMPLATE!
	</tr>
	</tbody>
</table>
"""

MESSAGE_STYLE_TEMPLATE = """<td style="text-align: left; vertical-align: top;"><div style="!MESSAGE_STYLE!">!MESSAGE!</div></td>"""
MESSAGE_NO_STYLE_TEMPLATE = """<td style="text-align: left; vertical-align: top;">!MESSAGE!</td>"""


IS_BACKGROUND_LIGHT = None

def test_if_background_is_light(style):

	bg = None
	style = style.strip()
	for e in style.split(';'):
		y = e.split(':')
		if len(y)==2:
			c = y[0].strip()
			if c.lower()=='background-color':
				bg = y[1].strip()

	if bg!=None:
		c = tuple(int(bg[i:i + 2], 16) / 255. for i in (1, 3, 5))
		luma = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
		luma = luma*100

		global IS_BACKGROUND_LIGHT
		if luma>=40:
			IS_BACKGROUND_LIGHT = True
		else:
			IS_BACKGROUND_LIGHT = False



def render_message(message,client=None):

	msg_to_display = message.contents

	if message.type!=PLUGIN_MESSAGE:
		# First, make sure that the message doesn't contain
		# any HTML formatting stuff; to do this, we escape all
		# HTML-relevant stuff so the message is *not* rendered
		# as HTML
		msg_to_display = html.escape(msg_to_display)

	if config.CLICKABLE_CHANNELS:
		if message.type!=SYSTEM_MESSAGE and message.type!=ERROR_MESSAGE and message.type!=PLUGIN_MESSAGE and message.type!=PLUGIN_SYSTEM_MESSAGE:
			try:
				d = []
				for w in msg_to_display.split():
					x = html.unescape(w)
					if x[:1]=='#' or x[:1]=='&' or x[:1]=='!' or x[:1]=='+':
						# Check to make sure the channel exists on the server; if the channel
						# doesn't exist, the channel link will not be created
						if client!=None:
							if x in client.channels and len(x)>1:
								o = "<a href=\""+x+"\" "
								o = o + "style=\""+STYLES["hyperlink"]+"\">"+x+"</a>"
								w = o

					if message.type==WHOIS_MESSAGE:
						if x[:1]=='+' or x[:1]=='@':
							y = x[1:]
							if y[:1]=='#' or y[:1]=='&' or y[:1]=='!' or y[:1]=='+':
								if client!=None:
									if y in client.channels and len(y)>1:
										o = "<a href=\""+y+"\" "
										o = o + "style=\""+STYLES["hyperlink"]+"\">"+x+"</a>"
										w = o

					d.append(w)
				msg_to_display = ' '.join(d)
			except:
				pass

	if config.CONVERT_URLS_TO_LINKS:
		msg_to_display = inject_www_links(msg_to_display,STYLES["hyperlink"])

	if config.DISPLAY_IRC_COLORS:
		if string_has_irc_formatting_codes(msg_to_display):
			msg_to_display = convert_irc_color_to_html(msg_to_display)
	else:
		msg_to_display = strip_color(msg_to_display)

	if config.FILTER_PROFANITY: msg_to_display = filterProfanityFromText(msg_to_display)

	if config.MARK_SYSTEM_MESSAGES_WITH_SYMBOL:
		if message.type==SYSTEM_MESSAGE:
			msg_to_display = config.SYSTEM_MESSAGE_PREFIX+" "+msg_to_display

	if config.MARK_SYSTEM_MESSAGES_WITH_SYMBOL:
		if message.type==PLUGIN_SYSTEM_MESSAGE:
			msg_to_display = config.SYSTEM_MESSAGE_PREFIX+" "+msg_to_display

	
	p = message.sender.split('!')
	if len(p)==2:
		nick = p[0]
	else:
		nick = message.sender

	if message.type==SYSTEM_MESSAGE:
		output = SYSTEM_TEMPLATE
		style = STYLES["system"]
	elif message.type==ERROR_MESSAGE:
		output = SYSTEM_TEMPLATE
		style = STYLES["error"]
	elif message.type==ACTION_MESSAGE:
		output = SYSTEM_TEMPLATE
		style = STYLES["action"]
	elif message.type==CHAT_MESSAGE:
		output = MESSAGE_TEMPLATE
		style = STYLES["message"]
	elif message.type==SELF_MESSAGE:
		output = MESSAGE_TEMPLATE
		style = STYLES["message"]
	elif message.type==NOTICE_MESSAGE:
		output = MESSAGE_TEMPLATE
		style = STYLES["message"]
	elif message.type==HORIZONTAL_RULE_MESSAGE:

		if IS_BACKGROUND_LIGHT==None:
			test_if_background_is_light(STYLES["all"])

		if IS_BACKGROUND_LIGHT==True:
			output = HORIZONTAL_RULE
		elif IS_BACKGROUND_LIGHT==False:
			output = LIGHT_HORIZONTAL_RULE
		else:
			output = HORIZONTAL_RULE

		#output = HORIZONTAL_RULE
		style = STYLES["message"]
	elif message.type==WHOIS_MESSAGE:
		output = MESSAGE_TEMPLATE
		style = STYLES["message"]
	elif message.type==PLUGIN_MESSAGE:
		output = SYSTEM_TEMPLATE
		style = STYLES["message"]
	elif message.type==DATE_MESSAGE:

		if IS_BACKGROUND_LIGHT==None:
			test_if_background_is_light(STYLES["all"])

		if IS_BACKGROUND_LIGHT==True:
			output = DATE_MESSAGE_TEMPLATE
		elif IS_BACKGROUND_LIGHT==False:
			output = LIGHT_DATE_MESSAGE_TEMPLATE
		else:
			output = DATE_MESSAGE_TEMPLATE

		#output = DATE_MESSAGE_TEMPLATE
		style = STYLES["message"]
	elif message.type==PLUGIN_SYSTEM_MESSAGE:
		output = SYSTEM_TEMPLATE
		style = STYLES["system"]

	if style=="":
		output = output.replace("!INSERT_MESSAGE_TEMPLATE!",MESSAGE_NO_STYLE_TEMPLATE)
	else:
		output = output.replace("!INSERT_MESSAGE_TEMPLATE!",MESSAGE_STYLE_TEMPLATE)
		output = output.replace("!MESSAGE_STYLE!",style)

	if config.DISPLAY_TIMESTAMP:

		if config.USE_24HOUR_CLOCK_FOR_TIMESTAMPS:
			tfs = '%H:%M'
		else:
			tfs = '%I:%M'

		if config.DISPLAY_TIMESTAMP_SECONDS:
			tfs = tfs + ':%S'

		pretty_timestamp = datetime.fromtimestamp(message.timestamp).strftime(tfs)

		ts = TIMESTAMP_TEMPLATE.replace("!TIMESTAMP_STYLE!",STYLES["timestamp"])
		ts = ts.replace("!TIME!",pretty_timestamp)

		output = output.replace("!TIMESTAMP!",ts)
	else:
		output = output.replace("!TIMESTAMP!",'')

	if message.type==SELF_MESSAGE:
		user_style = STYLES["self"]
	elif message.type==CHAT_MESSAGE:
		user_style = STYLES["username"]
	elif message.type==NOTICE_MESSAGE:
		user_style = STYLES["notice"]
	elif message.type==WHOIS_MESSAGE:
		user_style = STYLES["system"]
	else:
		user_style = ''

	# Pad nickname
	if message.type!=ACTION_MESSAGE:
		idl = config.NICK_DISPLAY_WIDTH - len(nick)
		if idl>0:
			nick = ('&nbsp;'*idl)+nick

	output = output.replace("!ID_STYLE!",user_style)
	output = output.replace("!ID!",nick)

	if message.type==ACTION_MESSAGE:
		output = output.replace("!MESSAGE!",nick +" " +msg_to_display)
	else:
		output = output.replace("!MESSAGE!",msg_to_display)


	# Handle hidden system messages
	if message.stype!=None:

		if message.stype==TYPE_MODE:
			if config.HIDE_MODE_DISPLAY:
				output = None

		if message.stype==TYPE_TOPIC:
			if config.HIDE_TOPIC_MESSAGE:
				output = None

		if message.stype==TYPE_QUIT:
			if config.HIDE_QUIT_MESSAGE:
				output = None

		if message.stype==TYPE_NICK:
			if config.HIDE_NICK_MESSAGE:
				output = None

		if message.stype==TYPE_INVITE:
			if config.HIDE_INVITE_MESSAGE:
				output = None

		if message.stype==TYPE_PART:
			if config.HIDE_PART_MESSAGE:
				output = None

		if message.stype==TYPE_JOIN:
			if config.HIDE_JOIN_MESSAGE:
				output = None

	return output

# URL LINKS

def inject_www_links(txt,style):

	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)
	for u in urls:
		u = re.sub('<[^<]+?>', '', u)
		link = f"<a href=\"{u}\"><span style=\"{style}\">{u}</span></a>"
		txt = txt.replace(u,link)
	return txt

# IRC COLOR CODES

def string_has_irc_formatting_codes(data):
	for code in ["\x03","\x02","\x1D","\x1F","\x0F"]:
		if code in data: return True
	return False

def convert_irc_color_to_html(text):

	html_tag = "font"

	# other format tags
	fout = ''
	inbold = False
	initalic = False
	inunderline = False
	incolor = False
	for l in text:
		if l=="\x02":
			inbold = True
			fout = fout + "<b>"
			continue
		if l=="\x1D":
			initalic = True
			fout = fout + "<i>"
			continue
		if l=="\x1F":
			inunderline = True
			fout = fout + "<u>"
			continue
		if l=="\x03":
			incolor = True
			fout = fout + l
			continue

		if l=="\x0F":
			if incolor:
				incolor = False
				fout = fout + f"</{html_tag}>"
				continue
			if inbold:
				fout = fout + "</b>"
				inbold = False
				continue
			if initalic:
				fout = fout + "</i>"
				initalic = False
				continue
			if inunderline:
				fout = fout + "</u>"
				inunderline = False
				continue

		fout = fout + l

	if inbold: fout = fout + "</b>"
	if initalic: fout = fout + "</i>"
	if inunderline: fout = fout + "</u>"

	text = fout

	combos = list(combinations(["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"],2))
	for c in combos:
		fore = c[0]
		back = c[1]

		if int(fore)==0: foreground = str(IRC_00)
		if int(fore)==1: foreground = str(IRC_01)
		if int(fore)==2: foreground = str(IRC_02)
		if int(fore)==3: foreground = str(IRC_03)
		if int(fore)==4: foreground = str(IRC_04)
		if int(fore)==5: foreground = str(IRC_05)
		if int(fore)==6: foreground = str(IRC_06)
		if int(fore)==7: foreground = str(IRC_07)
		if int(fore)==8: foreground = str(IRC_08)
		if int(fore)==9: foreground = str(IRC_09)
		if int(fore)==10: foreground = str(IRC_10)
		if int(fore)==11: foreground = str(IRC_11)
		if int(fore)==12: foreground = str(IRC_12)
		if int(fore)==13: foreground = str(IRC_13)
		if int(fore)==14: foreground = str(IRC_14)
		if int(fore)==15: foreground = str(IRC_15)

		if int(back)==0: background = str(IRC_00)
		if int(back)==1: background = str(IRC_01)
		if int(back)==2: background = str(IRC_02)
		if int(back)==3: background = str(IRC_03)
		if int(back)==4: background = str(IRC_04)
		if int(back)==5: background = str(IRC_05)
		if int(back)==6: background = str(IRC_06)
		if int(back)==7: background = str(IRC_07)
		if int(back)==8: background = str(IRC_08)
		if int(back)==9: background = str(IRC_09)
		if int(back)==10: background = str(IRC_10)
		if int(back)==11: background = str(IRC_11)
		if int(back)==12: background = str(IRC_12)
		if int(back)==13: background = str(IRC_13)
		if int(back)==14: background = str(IRC_14)
		if int(back)==15: background = str(IRC_15)

		t = f"\x03{fore},{back}"
		r = f"<{html_tag} style=\"color: {foreground}; background-color: {background}\">"
		text = text.replace(t,r)

	combos = list(combinations(["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15"],2))
	for c in combos:
		fore = c[0]
		back = c[1]

		if int(fore)==0: foreground = str(IRC_00)
		if int(fore)==1: foreground = str(IRC_01)
		if int(fore)==2: foreground = str(IRC_02)
		if int(fore)==3: foreground = str(IRC_03)
		if int(fore)==4: foreground = str(IRC_04)
		if int(fore)==5: foreground = str(IRC_05)
		if int(fore)==6: foreground = str(IRC_06)
		if int(fore)==7: foreground = str(IRC_07)
		if int(fore)==8: foreground = str(IRC_08)
		if int(fore)==9: foreground = str(IRC_09)
		if int(fore)==10: foreground = str(IRC_10)
		if int(fore)==11: foreground = str(IRC_11)
		if int(fore)==12: foreground = str(IRC_12)
		if int(fore)==13: foreground = str(IRC_13)
		if int(fore)==14: foreground = str(IRC_14)
		if int(fore)==15: foreground = str(IRC_15)

		if int(back)==0: background = str(IRC_00)
		if int(back)==1: background = str(IRC_01)
		if int(back)==2: background = str(IRC_02)
		if int(back)==3: background = str(IRC_03)
		if int(back)==4: background = str(IRC_04)
		if int(back)==5: background = str(IRC_05)
		if int(back)==6: background = str(IRC_06)
		if int(back)==7: background = str(IRC_07)
		if int(back)==8: background = str(IRC_08)
		if int(back)==9: background = str(IRC_09)
		if int(back)==10: background = str(IRC_10)
		if int(back)==11: background = str(IRC_11)
		if int(back)==12: background = str(IRC_12)
		if int(back)==13: background = str(IRC_13)
		if int(back)==14: background = str(IRC_14)
		if int(back)==15: background = str(IRC_15)

		t = f"\x03{fore},{back}"
		r = f"<{html_tag} style=\"color: {foreground}; background-color: {background}\">"
		text = text.replace(t,r)

	text = text.replace("\x0310",f"<{html_tag} style=\"color: {IRC_10};\">")
	text = text.replace("\x0311",f"<{html_tag} style=\"color: {IRC_11};\">")
	text = text.replace("\x0312",f"<{html_tag} style=\"color: {IRC_12};\">")
	text = text.replace("\x0313",f"<{html_tag} style=\"color: {IRC_13};\">")
	text = text.replace("\x0314",f"<{html_tag} style=\"color: {IRC_14};\">")
	text = text.replace("\x0315",f"<{html_tag} style=\"color: {IRC_15};\">")

	text = text.replace("\x0300",f"<{html_tag} style=\"color: {IRC_00};\">")
	text = text.replace("\x0301",f"<{html_tag} style=\"color: {IRC_01};\">")
	text = text.replace("\x0302",f"<{html_tag} style=\"color: {IRC_02};\">")
	text = text.replace("\x0303",f"<{html_tag} style=\"color: {IRC_03};\">")
	text = text.replace("\x0304",f"<{html_tag} style=\"color: {IRC_04};\">")
	text = text.replace("\x0305",f"<{html_tag} style=\"color: {IRC_05};\">")
	text = text.replace("\x0306",f"<{html_tag} style=\"color: {IRC_06};\">")
	text = text.replace("\x0307",f"<{html_tag} style=\"color: {IRC_07};\">")
	text = text.replace("\x0308",f"<{html_tag} style=\"color: {IRC_08};\">")
	text = text.replace("\x0309",f"<{html_tag} style=\"color: {IRC_09};\">")

	text = text.replace("\x030",f"<{html_tag} style=\"color: {IRC_00};\">")
	text = text.replace("\x031",f"<{html_tag} style=\"color: {IRC_01};\">")
	text = text.replace("\x032",f"<{html_tag} style=\"color: {IRC_02};\">")
	text = text.replace("\x033",f"<{html_tag} style=\"color: {IRC_03};\">")
	text = text.replace("\x034",f"<{html_tag} style=\"color: {IRC_04};\">")
	text = text.replace("\x035",f"<{html_tag} style=\"color: {IRC_05};\">")
	text = text.replace("\x036",f"<{html_tag} style=\"color: {IRC_06};\">")
	text = text.replace("\x037",f"<{html_tag} style=\"color: {IRC_07};\">")
	text = text.replace("\x038",f"<{html_tag} style=\"color: {IRC_08};\">")
	text = text.replace("\x039",f"<{html_tag} style=\"color: {IRC_09};\">")

	text = text.replace("\x03",f"</{html_tag}>")

	# close font tags
	if f"<{html_tag} style=" in text:
		if not f"</{html_tag}>" in text: text = text + f"</{html_tag}>"

	out = []
	indiv = False
	for w in text.split(' '):

		if indiv:
			if w==f"<{html_tag}":
				out.append(f"</{html_tag}>")

		if w==f"<{html_tag}": indiv = True
		if w==f"</{html_tag}>": indiv = False

		out.append(w)

	text = ' '.join(out)

	return text

def strip_color(text):

	html_tag = "font"

	combos = list(combinations(["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15"],2))
	for c in combos:
		fore = c[0]
		back = c[1]

		t = f"\x03{fore},{back}"
		text = text.replace(t,'')

	combos = list(combinations(["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15"],2))
	for c in combos:
		fore = c[0]
		back = c[1]

		t = f"\x03{fore},{back}"
		text = text.replace(t,'')

	text = text.replace("\x0310","")
	text = text.replace("\x0311","")
	text = text.replace("\x0312","")
	text = text.replace("\x0313","")
	text = text.replace("\x0314","")
	text = text.replace("\x0315","")

	text = text.replace("\x0300","")
	text = text.replace("\x0301","")
	text = text.replace("\x0302","")
	text = text.replace("\x0303","")
	text = text.replace("\x0304","")
	text = text.replace("\x0305","")
	text = text.replace("\x0306","")
	text = text.replace("\x0307","")
	text = text.replace("\x0308","")
	text = text.replace("\x0309","")

	text = text.replace("\x030","")
	text = text.replace("\x031","")
	text = text.replace("\x032","")
	text = text.replace("\x033","")
	text = text.replace("\x034","")
	text = text.replace("\x035","")
	text = text.replace("\x036","")
	text = text.replace("\x037","")
	text = text.replace("\x038","")
	text = text.replace("\x039","")

	text = text.replace("\x03","")

	text = text.replace("\x02","")
	text = text.replace("\x1D","")
	text = text.replace("\x1F","")
	text = text.replace("\x0F","")

	return text
