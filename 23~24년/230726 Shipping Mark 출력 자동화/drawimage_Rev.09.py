from PyPDF4 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from datetime import datetime

def select_pdf_file():
    download_folder = "C:\\Users\\LG\\Downloads"
    pdf_files = [f for f in os.listdir(download_folder) if f.endswith('.pdf')]
    print("사용 가능한 PDF 파일:")
    for idx, file in enumerate(pdf_files):
        print(f"{idx + 1}. {file}")
    choice = int(input("선택할 PDF 파일 번호를 입력하세요: ")) - 1
    return os.path.join(download_folder, pdf_files[choice])

def copy_pages(input_pdf_path, first_copies):
    reader = PdfFileReader(input_pdf_path)
    writer = PdfFileWriter()
    total_pages = reader.getNumPages()

    if total_pages not in [1, 2]:
        print("지원하지 않는 페이지 수입니다. 1페이지 또는 2페이지의 PDF만 지원됩니다.")
        return None

    if total_pages == 2: # 두 번째 페이지가 있으면 첫 번째 페이지 복사 수를 하나 줄임
        first_copies -= 1

    for _ in range(first_copies):
        writer.addPage(reader.getPage(0))
    if total_pages == 2: # 두 번째 페이지가 있을 때 한 장만 추가
        writer.addPage(reader.getPage(1))

    return writer

def add_watermark(input_pdf_path, type, current_document_number, total_documents):
    positions = {
        'UNICEF': (210, 80),
        'SPA': (298, 44),
        'JPNY': (234, 222),
        'EUHR': (248, 38),
        'CHNFA': (394, 326),
        'CHNF': (248, 44),
        'ENG': (248, 44)
    }
    reader = PdfFileReader(input_pdf_path)
    writer = PdfFileWriter()
    x_position, y_position = positions[type]
    total_pages = reader.getNumPages()
    for i in range(total_pages):
        page = reader.getPage(i)
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        page_number_text = f"{current_document_number + i}              {total_documents}"  # 전체 페이지 수를 출력
        can.drawString(x_position, y_position, page_number_text)
        can.save()
        packet.seek(0)
        watermark = PdfFileReader(packet)
        page.mergePage(watermark.getPage(0))
        writer.addPage(page)
    return writer

def select_type():
    type_options = ['UNICEF', 'SPA', 'JPNY', 'EUHR', 'CHNFA', 'CHNF', 'ENG']
    print("유형을 선택하세요:")
    for idx, option in enumerate(type_options):
        print(f"{idx + 1}. {option}")
    type_choice_idx = int(input("유형 번호를 입력하세요: ")) - 1

    if type_choice_idx < 0 or type_choice_idx >= len(type_options):
        raise ValueError("유효하지 않은 유형 번호입니다.")

    return type_options[type_choice_idx]

def main():
    total_documents = int(input("전체 문서 번호를 입력하세요 (예: 30): "))
    first_pdf_copies = int(input("첫 번째 출력되는 PDF 페이지 수를 입력하세요 (예: 20): "))

    if first_pdf_copies > total_documents:
        print("첫 번째 PDF 페이지 수는 전체 문서 번호보다 클 수 없습니다. 다시 시도해주세요.")
        return

    current_document_number = 1

    # 첫 번째 PDF 파일 처리
    selected_pdf_file = select_pdf_file()
    writer = copy_pages(selected_pdf_file, first_pdf_copies)
    if writer is None:
        print("PDF 생성에 실패하였습니다.")
    else:
        temp_pdf_file = os.path.join("C:\\Users\\LG\\Downloads", "temp.pdf")
        with open(temp_pdf_file, "wb") as temp_pdf:
            writer.write(temp_pdf)

        type_choice = select_type()

        # temp.pdf 파일에 워터마크 추가
        writer_with_watermark = add_watermark(temp_pdf_file, type_choice, current_document_number, total_documents)

        # 파일 이름에 current_document_number 추가
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        output_pdf_file = os.path.join("C:\\Users\\LG\\Downloads", f"{timestamp}_{current_document_number}.pdf")
        with open(output_pdf_file, "wb") as output_pdf:
            writer_with_watermark.write(output_pdf)

        print(f"페이지 번호가 추가된 파일이 저장되었습니다: {output_pdf_file}")

        # 다음 문서 번호로 업데이트
        current_document_number += first_pdf_copies + (1 if writer.getNumPages() == 2 else 0)

    # 두 번째 PDF 파일 처리 (첫 번째 PDF 파일이 전체 문서 번호를 채우지 않았을 경우)
    if current_document_number <= total_documents:
        second_pdf_copies = total_documents - current_document_number + 1
        selected_pdf_file = select_pdf_file()
        writer = copy_pages(selected_pdf_file, second_pdf_copies)

        # 두 번째 PDF 파일에 대한 나머지 처리
        temp_pdf_file = os.path.join("C:\\Users\\LG\\Downloads", "temp.pdf")
        with open(temp_pdf_file, "wb") as temp_pdf:
            writer.write(temp_pdf)

        type_choice = select_type()

        # temp.pdf 파일에 워터마크 추가
        writer_with_watermark = add_watermark(temp_pdf_file, type_choice, current_document_number, total_documents)
        
        # 파일 이름에 current_document_number 추가
        output_pdf_file = os.path.join("C:\\Users\\LG\\Downloads", f"{timestamp}_{current_document_number}.pdf")
        with open(output_pdf_file, "wb") as output_pdf:
            writer_with_watermark.write(output_pdf)

        print(f"페이지 번호가 추가된 파일이 저장되었습니다: {output_pdf_file}")

    print("모든 문서 번호가 추가되었습니다.")

if __name__ == "__main__":
    main()

