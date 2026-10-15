from pathlib import Path
import shutil
import pymupdf as f

root=Path(r'D:\kmj\flask\project_TripPalette')
path=root/'TripPalette_Portfolio.pdf'
backup=root/'output/pdf/TripPalette_Portfolio_before_inset_edit.pdf'
if not backup.exists(): shutil.copy2(path,backup)
src=f.open(root/'output/pdf/TripPalette_Portfolio_before_banner_edit.pdf')
doc=f.open(root/'output/pdf/TripPalette_Portfolio_before_banner_edit.pdf')
background=f.open()
bgpage=background.new_page(width=960,height=540)
bgpage.insert_image(bgpage.rect,filename=r'C:\Users\404_27\.codex\generated_images\01a1140b-97d2-7c43-8f60-facca7e59054\exec-085f3992-8102-4e86-a1af-977ab3d68fb4.png',keep_proportion=False)

def shift(page,index,clip,blank):
    strip=f.Rect(clip.x0,clip.y0,clip.x0+12,clip.y1)
    page.show_pdf_page(strip,src,index,clip=blank,keep_proportion=False)
    target=clip+f.Rect(12,0,12,0)
    page.show_pdf_page(target,src,index,clip=clip)

shift(doc[0],0,f.Rect(68,65,399,245),f.Rect(535,65,547,245))
qr=f.Rect(410,183,510,245)
doc[0].show_pdf_page(qr,src,0,clip=qr)
for index in range(1,15):
    p=doc[index]
    header=f.Rect(0,0,960,124)
    p.show_pdf_page(header,background,0,clip=header)
    p.show_pdf_page(f.Rect(154,62,636,120),src,index,clip=f.Rect(118,55,600,113))
    p.draw_rect(f.Rect(108,69,143,96),radius=.3,color=None,fill=(1,.40,.16))
    p.insert_text((116,88),str(index+1).zfill(2),fontname='hebo',fontsize=13,color=(1,1,1))

page=doc[15]
paper=(0.989,0.980,0.956)
# Keep the inset inside the original rounded border, including both top corners.
shape=page.new_shape()
shape.draw_line(f.Point(49,33),f.Point(911,33))
shape.draw_bezier(f.Point(911,33),f.Point(923,33),f.Point(931,41),f.Point(931,53))
shape.draw_line(f.Point(931,53),f.Point(931,166))
shape.draw_line(f.Point(931,166),f.Point(29,166))
shape.draw_line(f.Point(29,166),f.Point(29,53))
shape.draw_bezier(f.Point(29,53),f.Point(29,41),f.Point(37,33),f.Point(49,33))
shape.finish(color=None,fill=paper,closePath=True)
shape.commit()
logo=f.Rect(667,54,896,114)
page.show_pdf_page(logo,src,14,clip=logo)
page.draw_rect(f.Rect(88,63,123,90),radius=0.3,color=None,fill=(1,.40,.16))
page.draw_line(f.Point(29,123),f.Point(931,123),color=(.44,.35,.27),width=.7)
page.insert_font(fontname='kb',fontfile=r'C:\Windows\Fonts\malgunbd.ttf')
page.insert_font(fontname='kr',fontfile=r'C:\Windows\Fonts\malgun.ttf')
page.insert_text((96,82),'16',fontname='hebo',fontsize=14,color=(1,1,1))
page.insert_text((139,81),'회고와 향후 개선',fontname='kb',fontsize=24,color=(.19,.16,.13))
page.insert_text((159,100),'구현 개수보다 중요한 것은, 실패해도 다시 일관된 상태로 돌아오는 구조였습니다.',fontname='kr',fontsize=10,color=(.48,.41,.35))
out=root/'tmp/pdfs/refined.pdf'
doc.save(out,garbage=3,deflate=True)
doc.close()
check=f.open(out)
assert len(check)==18
for i in range(1,15):
    assert check[i].get_pixmap(clip=f.Rect(0,124,960,540)).samples==src[i].get_pixmap(clip=f.Rect(0,124,960,540)).samples
assert check[0].get_pixmap(clip=f.Rect(0,246,960,540)).samples==src[0].get_pixmap(clip=f.Rect(0,246,960,540)).samples
assert check[15].get_pixmap(clip=f.Rect(0,167,960,540)).samples==src[15].get_pixmap(clip=f.Rect(0,167,960,540)).samples
for i in [16,17]: assert check[i].get_pixmap().samples==src[i].get_pixmap().samples
for i in [0,1,14,15,16]:
    check[i].get_pixmap(matrix=f.Matrix(1.5,1.5)).save(root/f'tmp/pdfs/refined-{i+1}.png')
shutil.copy2(out,path)
print('Verified header insets, preserved body content and pages 17-18.')
