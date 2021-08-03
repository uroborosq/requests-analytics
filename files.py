import openpyxl
from openpyxl import styles
import json


class DaySchedule(object):
    def __init__(self, data, date):
        self.date = date
        wb = openpyxl.Workbook()
        worksheet = wb['Sheet']
        worksheet['B2'] = 'Дата'
        worksheet['C2'] = str(date.strftime('%d-%m-%Y'))
        for i in ['A', 'B', 'C', 'D', 'E']:
            worksheet.merge_cells(i + '4:' + i + '5')
        worksheet.merge_cells('F4:K4')
        worksheet.merge_cells('L4:M4')

        tmp = {'A4': '№ п/п', 'B4': '№ наряд-заказа', 'C4': 'Исполнитель', 'D4': 'Гарантия/внутр/платно',
               'E4': 'ЗИП потратил', 'F4': 'В электронном виде прислал', 'F5': 'Описание работ', 'G5': 'Наряд-заказ',
               'H5': 'Гарталон', 'I5': 'Сер номер', 'J5': 'Деталь', 'K5': 'Шильда', 'L4': 'В бумажном виде',
               'L5': 'Наряд-заказ', 'M5': 'Накладные'}
        for i in tmp:
            worksheet[i] = tmp[i]
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = cell.alignment.copy(wrapText=True)
        tmp = {'A': 4, 'B': 11, 'C': 30, 'D': 20, 'E': 12, 'F': 15, 'G': 12, 'H': 11, 'I': 11, 'L': 12, 'M': 11}

        worksheet['F4'].alignment = styles.Alignment(horizontal="center")
        worksheet['L4'].alignment = styles.Alignment(horizontal="center")
        for i in tmp:
            cl = worksheet.column_dimensions[i]
            cl.width = tmp[i]

        counter = 1
        for i in data:
            for j in data[i]:
                worksheet['A' + str(counter + 5)] = counter
                worksheet['B' + str(counter + 5)] = j[0]
                worksheet['C' + str(counter + 5)] = i
                worksheet['D' + str(counter + 5)] = j[1]
                counter += 1

        for i in range(counter - 1):
            rw = worksheet.row_dimensions[i + 6]
            rw.height = 60

        tmp = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
        for i in range(13):
            for j in range(counter - 1):
                tmp.append(tmp[i] + str(j + 6))

        for i in ['B2', 'C2', 'A4', 'B4', 'C4', 'D4', 'E4', 'F4', 'F5', 'G5', 'H5', 'I5', 'J5', 'K5', 'L4', 'L5', 'M5',
                  'A5', 'B5', 'C5', 'D5', 'E5', 'M4', 'G4', 'H4', 'I4', 'J4'] + tmp[13:]:
            worksheet[i].border = styles.Border(top=styles.Side(border_style="thin", color="000000"),
                                                left=styles.Side(border_style="thin", color="000000"),
                                                right=styles.Side(border_style="thin", color="000000"),
                                                bottom=styles.Side(border_style="thin", color="000000"))
        for i in tmp[13:]:
            worksheet[i].alignment = styles.Alignment(horizontal='center', vertical='center')
        wb.save('DaySchedule' + str(date.strftime('%d-%m-%Y')) + '.xlsx')

    def get(self):
        return 'DaySchedule' + str(self.date.strftime('%d-%m-%Y')) + '.xlsx'


def return_dict():
    return {
            'id': 'B',
            'date_begin': 'E',
            'date_begin_working': 'F',
            'date_end': 'H',
            'status': 'I',
            'manager': 'J',
            'type': 'L',
            'phase': 'M',
            'engineer': 'N',
            'client': 'O',
            'address': 'P',
            'model': 'K',
            'priority': 'R',
            'lines_to_skip': '6'
    }


def set_default():
    file = open('.parser_settings.json', 'w')
    settings = return_dict()
    json.dump(settings, file, indent=4)
    file.close()
    return settings


def return_number():
    return len(return_dict())
