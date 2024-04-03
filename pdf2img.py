import fitz  # PyMuPDF
import os


class PDFTransformer:
    def __init__(self):
        self.pdf_path = ''
        self.dpi = 300
        self.pdf_filename = ''
        self.output_folder = ''

    def pdf2img(self, pdf_path):
        # 指定 PDF 文件路径
        self.pdf_path = pdf_path

        # 获取 PDF 文件名（不带扩展名）
        self.pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]

        # 创建以 PDF 文件名命名的文件夹
        self.output_folder = os.path.join('output', self.pdf_filename)
        os.makedirs(self.output_folder, exist_ok=True)

        # 打开 PDF 文件
        pdf_document = fitz.open(pdf_path)

        # 定义输出图片的 DPI
        dpi = self.dpi  # 调整这个值以达到更高的分辨率

        # 定义输出图片的缩放因子为1
        scale_factor = 1.0

        # 遍历每一页，并保存为图片
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]

            # 计算输出图片的像素大小
            width, height = int(page.rect.width * dpi / 72.0), int(page.rect.height * dpi / 72.0)

            # 创建一个以指定大小的 Pixmap
            image = page.get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0), clip=fitz.Rect(0, 0, width, height))

            # 保存图片
            image.save(os.path.join(self.output_folder, f'{self.pdf_filename}-{page_number + 1}.png'), 'PNG')


        # 关闭 PDF 文件
        pdf_document.close()

