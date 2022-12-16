from math import sqrt
from PIL import Image, ImageDraw, ImageFont
from sys import platform

if platform == "darwin":
    arial='/Library/Fonts/Arial.ttf' # Apple fonts location
elif platform =="linux":
    arial='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf' # Ubuntu fonts location
else:
    pass

def svg_viewbox(window_x, window_y, window_w, window_h, screen_w, screen_h, content=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{window_x} {window_y} {window_w} {window_h}" width="{screen_w}" height="{screen_h}" > {content} </svg>"""

def svg_rect(x,y,w,h, content=""):
    return f"""<rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="black" stroke-width="1" fill="green" opacity="0.85"> {content} </rect>"""

def panel_outline(x,y,w,h,r,th):
    title_path = f"M {x} {y+(th)} L {x} {y+r} Q {x} {y} {x+r} {y} L {x+w-r} {y} Q {x+w} {y} {x+w} {y+r} L {w+x} {y+th} Z"
    canvas_path = f"M {x+w} {y+th} L {x+w} {y+h-r} Q {x+w} {y+h} {x+w-r} {y+h} L {x+r} {y+h} Q {x} {y+h} {x} {y+h-r} L {x} {y+th} Z"
    return f"""<path d="{title_path}" stroke="black" stroke-width="1" fill="pink" opacity="1.00" />""" + \
           f"""<path d="{canvas_path}" stroke="black" stroke-width="1" fill="white" opacity="1.00" />"""

def titled_panel(x,y,w,h,r,th,text,oversize_method="truncate"):
    cpath = panel_outline(x,y,w,h,r,th)
    title_rect = (x+r, y+(r/2), w-(2*r), th-r)
    t_box = text_rectangle(text, title_rect, oversize_method)
    return cpath + t_box

def graphicaltextsize(text, fontsize=14):
    image = Image.new("RGB", (20,20))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(arial, fontsize)
    bbox = draw.textbbox((0,0), text, font)
    return (bbox[2], bbox[3])

def fontmetrics(text, fontsize=14):
    font = ImageFont.truetype(arial, fontsize)
    ascent, descent = font.getmetrics()
    (width, baseline), (offset_x, offset_y) = font.font.getsize(text)
    return width, ascent + descent - offset_y, baseline

def text_rectangle(text, rectangle, oversize_method="truncate"):
    fontsize = 32
    x,y,w,h = rectangle
    ptext,ph = prepare_text(text, (w*1.6, h), oversize_method)
    refbb = graphicaltextsize(ptext, fontsize)
    fw,fh,fb = fontmetrics(ptext, fontsize)
    rw, rh = refbb
    scale_x, scale_y = w/rw, h/rh
    loc_y = (fb * scale_y)
    morph = scale_x/scale_y
    if morph > 2:
        scale_x = scale_x / morph

    stext = ptext.split("\n")
    l_height = rh/len(stext)
    spans = [f"""<tspan x="0" y="%%yoffset%%" >{s} </tspan> \n""" for e,s in enumerate(stext)]
    offsets=[]
    for e,l in enumerate(stext):
        offsets.append((0, e * l_height))
    spans = [l.replace("%%yoffset%%", str(offsets[e][1])) for e,l in enumerate(spans)]
    return f"""<g transform="matrix({scale_x} 0 0 {scale_y} {x} {y+loc_y})" ><text x="{0}" y="{0}" style="font-size:{fontsize};"><title>{text}</title>{"".join(spans)}</text>\n</g>"""



def scorechar(c, loc, target, bchars):
    score=0
    adj=1/target
    neg=0
    if c in bchars:
        if loc>target:
            neg=((loc-target)**3)
        score = 1 / ((( loc-target) **2 ) + 1 + neg)
    else:
        score = 1 / ((( loc-target) **2 ) + 1) *(adj**2)
    return score

def word_wrap(text, target_length):
    linespace = 1.2
    breakchars = " ,.-"
    delchars = "\n\t"
    for c in delchars:
        text = text.replace(c," ")
    best_split = 0
    texts = []
    finished=False
    stext = "".join([t for t in text])
    while not finished and len(stext)!=0:
        osp = [scorechar(c,e,target_length, breakchars) for e,c in enumerate(stext)]
        best_split = osp.index(max(osp))

        if len(stext)==0 or best_split==0 or (target_length*linespace)>=len(stext):
            texts.append(stext)
            finished=True
        else:
            texts.append(stext[:best_split+1])
        stext = stext[best_split+1:]
    return texts

def prepare_text(text, bounding_box, oversize_method="wrap"):

    linespace=1.2
    tw, th, tb = fontmetrics(text)
    th = th*linespace
    tar = tw/th
    bw, bh = bounding_box
    bar = bw/bh
    aspect = tar/bar
    cw = len(text)
    text_height = 1
    if aspect > 1.2:
        if oversize_method.lower()=="wrap":
            wt = int(cw/sqrt(tar/bar))
            ww = word_wrap(text, wt)
            return "\n".join(ww), (bh/len(ww))/linespace
        elif oversize_method.lower()=="truncate":
            return text[:int(cw*(bw/tw))-3]+"...", bh
    elif aspect < 0.8:
        return text, bw/tar
    else:
        return text, bw/tar
