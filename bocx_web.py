#!/usr/bin/python3

from flask import Flask, render_template, request
from Adafruit_Thermal import *

'''
d_billEntry = {
        'shopName':'Name of Shop',
        'items':[
                    {'itemName':'item 1',       'qty':5,    'rate':10},
        ],
        'msg':'Thank you for shopping with us',
}
'''
VER = "1.2.0"
MAX_COL = 31

billNo = ""
date = ""

def main():
    print("Bocx PC ver %s"%(VER))
    tp = Adafruit_Thermal("/dev/ttyUSB0", 19200, timeout=5)
    d_billEntry = bbGetData()
    if(d_billEntry == False):
        return
    bbPrintBill(tp, d_billEntry)

def bbGetData():
    itemList = []
    global billNo
    global date

    shopName = input('Name of Shop: ')
    if(bbValidate(shopName)!=0):
        bbError()
        return False

    shopAdr = input('Address of Shop: ')
    if(bbValidate(shopAdr)!=0):
        bbError()
        return False

    billNo = input('Bill No: ')
    if(bbValidate(billNo)!=0):
        bbError()
        return False

    date = input('Date: ')
    if(bbValidate(date)!=0):
        bbError()
        return False

    opt = input('Do you want to continue billing (y/n):')
    if(opt.lower() == 'n'):
        return False
    num = 1
    while True:
        itemName = input('Item(%d): '%(num))
        qty = input('Quantity(%d): '%(num))
        qty = int(qty)
        rate = input('Rate(%d): '%(num))
        rate = float(rate)
        itemList.append({'itemName':itemName,       'qty':qty,    'rate':rate})

        opt = input('Do you want to enter another item (y/n):')
        if(opt.lower() == 'n'):
            break
        num+=1

    opt = input('Do you want to enter a message\n(y)es/(n)o/(d)fault\n ')
    if(opt.lower() == 'y'):
        shopMsg = input('Enter a message(32 char): ')
        if(bbValidate(shopName)!=0):
            bbError()
            return False
    elif(opt.lower() == 'd'):
        shopMsg = "Thank you for shopping with us"
    elif(opt.lower() == 'n'):
        shopMsg = ""
    else:
        shopMsg = "Thank you for shopping with us"

    return {
        'shopName':shopName,
        'shopAdr':shopAdr,
        'items':itemList,
        'msg':shopMsg,
    }
    


def bbValidate(data, max_len=32, min_len=1,vType=str):
    if(len(data)>max_len):
        return -1

    if(len(data)<min_len):
        return -1

    if(vType!=type(data)):
        return -1

    return 0

def bbError(err = ''):
    print('[Error]: '+str(err))

def bbCustomFormatter(entry):
    output = "-------------------------------"
    if( len( entry['itemName'] ) > 13 ):
        output = ' '+entry['itemName']+'\n' #1
        output += '              '
    else:
        output = ' '+entry['itemName'] #1
    output += ' '*(14-len(output))

    s_qty = str(entry['qty'])
    output += ' '*(3-len(s_qty))+s_qty #14
    output += ' '*(18-len(output))

    s_rate = "%.2f"%(entry['rate'])
    output += ' '*(6-len(s_rate))+s_rate #18
    output += ' '*(25-len(output))

    s_total = "%.2f"%(float(entry['qty'])*entry['rate'])
    output += ' '*(6-len(s_total))+s_total
#    output +=  # 25

    return output

QTY_IDX = 10
RATE_IDX = 16
PRICE_IDX = 23

def bbCustomFormatter2(entry):
    output = "-------------------------------"
# first line
    output = ' '+entry['itemName'] #1
    output += ' '*(MAX_COL-len(output))
# second line
    spaceLine = ' '*(MAX_COL)
    spaceLine = spaceLine[:QTY_IDX-1] + str(entry['qty']) + spaceLine[QTY_IDX+len(str(entry['qty'])):]

    s_rate = "%.2f"%(entry['rate'])
    spaceLine = spaceLine[:RATE_IDX-1] + s_rate + spaceLine[RATE_IDX+len(s_rate):]

    s_total = "%.2f"%(float(entry['qty'])*entry['rate'])
    spaceLine = spaceLine[:PRICE_IDX-1] + s_total + spaceLine[PRICE_IDX+len(s_total):]
    output += spaceLine

    return output

def bbPrintBillDbg(printer, d_billEntry):
    print('<JC>')
    print('<U>',end='')
    print('<H1>',end='')
    print(d_billEntry['shopName'],end='')
    print('</H1>',end='')
    print('</U>')
    print('<JL>')

    print("-------------------------------")
    print(" Item   Qty   Rate   Price     ")
    print("-------------------------------")

    total = 0
    for item in d_billEntry['items']:
        print(bbCustomFormatter(item))
        total += (item['qty']*item['rate'])
    
    print("-------------------------------")
    print(" Total:                  %s"%(s_total))
    print("-------------------------------")
    print(d_billEntry['msg'])

    print(">")
    print(">")


def bbPrintBill(printer, d_billEntry):
    global billNo
    global date

    printer.justify('C')
    printer.setSize('L')
    printer.println(d_billEntry['shopName'])
    printer.setSize('S')
    printer.println(d_billEntry['shopAdr'])
    printer.justify('L')

    printer.println(" Bill No: %s"%(billNo))
    printer.println(" %s"%(date))
    printer.println("-------------------------------")
    printer.println(" Item   Qty   Rate   Price     ")
    printer.println("-------------------------------")

    total = 0
    for item in d_billEntry['items']:
        printer.println(bbCustomFormatter2(item))
        total += (float(item['qty'])*float(item['rate']))
    s_total = "%.2f"%(total)
    s_total = ' '*(6-len(s_total))+s_total

    printer.println("-------------------------------")
    printer.println(" Total:              %.2f"%(total))
    printer.println("-------------------------------")

    printer.justify('C')
    printer.println(d_billEntry['msg'])
    printer.justify('L')

    printer.feed(3)

    printer.sleep()      # Tell printer to sleep
    printer.wake()       # Call wake() before printing again, even if reset
    printer.setDefault() # Restore printer to defaults

'''
if __name__ == '__main__':
    main()
'''


app = Flask(__name__)

def bbWebGetData( result ):
    global billNo
    global date

    total_data_len = len(result)
    total_item_count = ( total_data_len - 4 ) / 3 # Magic number alert !

    print("data count: %f"%(total_item_count))

    shopName = result['shop_name']
    shopAdr = result['address']
    billNo = result['bill_no']
    date = result['date']
    itemList = []
    shopMsg = result['shop_message']

    for i in range( 1, int(total_item_count) + 1 ):
        itemList.append(
            {
            'itemName'  :result[ 'item_name_' + str(i) ],       
            'qty'       :int( result['item_qty_' + str(i)] ),    
            'rate'      :float( result['item_rate_' +str(i)] )
            }
        )

    return {
        'shopName'  :shopName,
        'shopAdr'   :shopAdr,
        'items'     :itemList,
        'msg'       :shopMsg,
    }

@app.route('/')
def student():
   return render_template('index.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        print( len(result) )
        tp = Adafruit_Thermal("/dev/ttyUSB0", 19200, timeout=5)
        d_billEntry = bbWebGetData( result )
        if(d_billEntry == False):
            return render_template("response.html",result = {} )
        bbPrintBill(tp, d_billEntry)
    return render_template("response.html",result = result)


if __name__ == '__main__':
    print("Bocx PC ver %s"%(VER))
    app.run('0.0.0.0',6969)


'''
itemList.append({'itemName':itemName,       'qty':qty,    'rate':rate})

    return {
        'shopName':shopName,
        'shopAdr':shopAdr,
        'items':itemList,
        'msg':shopMsg,
    }
'''