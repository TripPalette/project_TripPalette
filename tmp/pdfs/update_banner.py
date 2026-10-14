from pathlib import Path
import shutil
import pymupdf as fitz
from PIL import Image, ImageChops

root = Path(r'D:\kmj\flask\project_TripPalette')
original = root / 'TripPalette_Portfolio.pdf'
backup = root / 'output/pdf/TripPalette_Portfolio_before_banner_edit.pdf'
backup.parent.mkdir(parents=True, exist_ok=True)
if not backup.exists():
    shutil.copy2(original, backup)
doc = fitz.open(backup)
source = fitz.open(backup)
page = doc[15]
paper = (0.989, 0.980, 0.956)
page.draw_rect(fitz.Rect(27, 32, 933, 166), color=None, fill=paper, overlay=True)
# Reuse the clean badge and logo crops without the source page's corner artwork.
for clip in [fitz.Rect(667, 54, 896, 114)]:
    page.show_pdf_page(clip, source, 14, clip=clip, overlay=True)
page.draw_rect(fitz.Rect(72, 60, 107, 87), radius=0.3, color=None,
               fill=(1.0, 0.40, 0.16), overlay=True)
page.draw_line(fitz.Point(27, 123), fitz.Point(933, 123),
               color=(0.44, 0.35, 0.27), width=0.7, overlay=True)
page.draw_rect(fitz.Rect(119, 52, 658, 112), color=None, fill=paper, overlay=True)
page.draw_rect(fitz.Rect(79, 64, 100, 83), color=None,
               fill=(1.0, 0.40, 0.16), overlay=True)
page.insert_font(fontname='koreanbold', fontfile=r'C:\Windows\Fonts\malgunbd.ttf')
page.insert_font(fontname='korean', fontfile=r'C:\Windows\Fonts\malgun.ttf')
page.insert_text((80, 79), '16', fontname='hebo', fontsize=14,
                 color=(1, 1, 1), overlay=True)
page.insert_text((123, 78), '회고와 향후 개선', fontname='koreanbold',
                 fontsize=24, color=(0.19, 0.16, 0.13), overlay=True)
page.insert_text((123, 97), '구현 개수보다 중요한 것은, 실패해도 다시 일관된 상태로 돌아오는 구조였습니다.',
                 fontname='korean', fontsize=10, color=(0.48, 0.41, 0.35), overlay=True)
temp = root / 'tmp/pdfs/updated.pdf'
doc.save(temp, garbage=3, deflate=True)
doc.close()
shutil.copy2(temp, original)
updated = fitz.open(original)
updated[15].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(root / 'tmp/pdfs/page-16-updated.png')
assert len(updated) == len(source) == 18
for index in range(18):
    if index == 15:
        continue
    assert updated[index].get_pixmap().samples == source[index].get_pixmap().samples, index
old_image = Image.open(root / 'tmp/pdfs/page-16.png').convert('RGB')
new_pix = updated[15].get_pixmap()
new_image = Image.frombytes('RGB', (new_pix.width, new_pix.height), new_pix.samples)
assert ImageChops.difference(old_image.crop((0, 167, 960, 540)), new_image.crop((0, 167, 960, 540))).getbbox() is None
print('Verified: 18 pages; only page 16 header changed; body preserved.')
