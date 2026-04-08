#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import os
import win32com.client as win32
from config import EXCEL_PATH,LOG_FILE

import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + "\n")
    except:
        pass

def load_json_data(json_filepath):
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data,dict):
            if 'new_record' in data:
                new_record = data.get('new_record', {})
                log(f"Новая запись: {new_record.get('product_name')}")
                return [new_record]
            else:
                print(f"⚠️ Неизвестный формат словаря")
                return []
    except FileNotFoundError:
        log(f"❌ Файл не найден: {json_filepath}")
        return []
    except json.JSONDecodeError as e:
        log(f"❌ Ошибка формата JSON: {e}")
        return []

def get_total_records(json_filepath):
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data,dict):
            if 'total_records' in data:
                total_records = data.get('total_records', 0)
                print(f"Всего записей={total_records}")
                return total_records
            else:
                print(f"⚠️ Неизвестный формат словаря")
                return 0
    except FileNotFoundError:
        log(f"❌ Файл не найден: {json_filepath}")
        return 0
    except json.JSONDecodeError as e:
        log(f"❌ Ошибка формата JSON: {e}")
        return 0

def calculate_profit(sales_data):
    profit_by_group = {}
    
    for sale in sales_data: 
        group = sale.get('product_group', 'Без группы')
        quantity = sale.get('quantity', 0)
        sale_price = sale.get('sale_price', 0)
        purchase_price = sale.get('purchase_price', 0)

        profit = (sale_price * quantity) - (purchase_price * quantity)
        profit_by_group[group] = profit_by_group.get(group, 0) + profit
    
    log("💰 Прибыль по группам:")
    for group, profit in profit_by_group.items():
        log(f"   {group}: {profit:.2f} руб.")
    
    return profit_by_group
    

def update_profit(profit_by_group,excel_path):
    try:
        log(f"🔌 Подключение к Excel...")
        excel = win32.Dispatch('Excel.Application')
        excel.Visible = False

        workbook = excel.Workbooks.Open(excel_path)
        sheet = workbook.Worksheets('Sheet1')

        
        for group,profit in profit_by_group.items():
            log(f"📝 Обработка группы: {group}, прибыль: {profit:.2f}")

            found = False
            row = 2
            while True:
                cell_value = sheet.Cells(row, 1).Value
                if cell_value is None or cell_value == '':
                    break
                if str(cell_value).strip() == group:
                    current_profit = sheet.Cells(row, 2).Value or 0
                    new_total = float(current_profit) + profit
                    sheet.Cells(row, 2).Value = new_total
                    log(f"   ✅ Обновлено: {group} = {new_total:.2f} (было {current_profit:.2f})")
                    found = True
                    break
                row+=1
            
            if not found:
                sheet.Cells(row, 1).Value = group
                sheet.Cells(row, 2).Value = profit
                log(f"   ✅ Добавлена новая группа: {group} = {profit:.2f}")
        
        
        workbook.RefreshAll()
        log(f"✅ Excel обновлен!")
        return True
    except Exception as e:
        log(f"❌ Ошибка Excel: {e}")
        import traceback
        log(traceback.format_exc())
        return False

def update_sales(sales_data,excel_path,total_records):
    try:
        log(f"🔌 Подключение к Excel...")
        excel = win32.Dispatch('Excel.Application')
        excel.Visible = False

        workbook = excel.Workbooks.Open(excel_path)
        sheet = workbook.Worksheets('Sheet2')

        row =total_records+1
        for sale in sales_data: 
            name = sale.get('product_name', '')
            group = sale.get('product_group', '')
            quantity = sale.get('quantity', 0)
            sale_price = sale.get('sale_price', 0)
            purchase_price = sale.get('purchase_price', 0)
            discount = sale.get('discount', 0)
            
            sheet.Cells(row, 1).Value = name
            sheet.Cells(row, 2).Value = group
            sheet.Cells(row, 3).Value = float(quantity)
            sheet.Cells(row, 4).Value = float(sale_price)
            sheet.Cells(row, 5).Value = float(purchase_price)
            sheet.Cells(row, 6).Value = float(discount)
            
            row += 1
        workbook.RefreshAll()
        excel.Visible = True
        log(f"✅ Excel обновлен! Добавлено {len(sales_data)} записей")
        return True
    except Exception as e:
        log(f"❌ Ошибка Excel: {e}")
        import traceback
        log(traceback.format_exc())
        return False


    

def clear_excel(excel_path):
    try:
        log(f"🔌 Подключение к Excel...")
        excel = win32.Dispatch('Excel.Application')
        excel.Visible = False

        workbook = excel.Workbooks.Open(excel_path)
        sheet1 = workbook.Worksheets('Sheet1')
        sheet2 = workbook.Worksheets('Sheet2')
        
        sheet1.Range('B2:B10').ClearContents()
        sheet2.Range('A2:F100').ClearContents()

        workbook.RefreshAll()
        excel.Visible = True
        
        log(f"✅ Excel очищен!")
        return True

    except Exception as e:
        log(f"❌ Ошибка очистки Excel: {e}")
        return False

def main():
    log('server работает')
    if len(sys.argv) < 2:
        log("❌ Ошибка: не указан путь к JSON файлу")
        log("Использование: python server.py <путь_к_json>")
        return
    
    json_file_path = sys.argv[1]
    excel_path = EXCEL_PATH

    log(f"📁 JSON: {json_file_path}")
    log(f"📊 Excel: {excel_path}")

    if not os.path.exists(json_file_path):
        log(f"❌ Файл не найден: {json_file_path}")
        return
    
    sales_data = load_json_data(json_file_path)
    total = get_total_records(json_file_path)

    if not sales_data:
        filename = os.path.basename(json_file_path)
        if filename.startswith('temp_') or filename.startswith('full_'):
            log("🗑️ Очищаем Excel (данных нет)")
            clear_excel(excel_path)
        if filename.startswith('temp_'):
            try:
                os.remove(json_file_path)
                log(f"🗑️ Удален пустой файл: {json_file_path}")
            except Exception as e:
                log(f"⚠️ Не удалось удалить: {e}")
        return

    profit_by_group = calculate_profit(sales_data)

    if not profit_by_group:
        log("⚠️ Нет данных для записи")
        return
    
    update_profit(profit_by_group,excel_path)
    update_sales(sales_data,excel_path,total)

    filename = os.path.basename(json_file_path)
    if filename.startswith('temp_') or filename.startswith('full_'):
        try:
            os.remove(json_file_path)
            log(f"🗑️ Удален временный файл: {json_file_path}")
        except Exception as e:
            log(f"⚠️ Не удалось удалить: {e}")
    else:
        log(f"💾 Файл сохранен: {json_file_path}")
    
    log("server завершил работу\n")


    

if __name__ == '__main__':
    main()
