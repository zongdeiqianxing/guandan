import cv2,numpy
import win32gui,win32ui,win32con,win32api
import os,prettytable,tkinter,time

screenshotFile = r'C:\Users\Public\screenshot.bmp'
cards={'2':8,'3':8,'4':8,'5':8,'6':8,'7':8,'8':8,'9':8,'10':8,'J':8,'Q':8,'K':8,'A':8,'W':4}
restarted = False
out_order = 0
isZero=[0,0,0,0,0]
threshold = 0.05

def screenshot():
	# 获取桌面
	hdesktop = win32gui.GetDesktopWindow()
	# 分辨率适应
	width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
	height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
	left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
	top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
	# 创建设备描述表
	desktop_dc = win32gui.GetWindowDC(hdesktop)
	img_dc = win32ui.CreateDCFromHandle(desktop_dc)
	# 创建一个内存设备描述表
	mem_dc = img_dc.CreateCompatibleDC()
	# 创建位图对象
	screenshot = win32ui.CreateBitmap()
	screenshot.CreateCompatibleBitmap(img_dc, width, height)
	mem_dc.SelectObject(screenshot)
	# 截图至内存设备描述表
	mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
	# 将截图保存到文件中
	screenshot.SaveBitmapFile(mem_dc,screenshotFile)
	# 内存释放
	mem_dc.DeleteDC()
	win32gui.DeleteObject(screenshot.GetHandle())
	
def matchSelfCards():
	target = cv2.imread(screenshotFile,cv2.IMREAD_GRAYSCALE)
	target = target[820:860,335:1275]
	x,target = cv2.threshold(target,230,255,cv2.THRESH_BINARY)	#230为红色扑克二值后与黑色扑克同识别
	#cv2.imshow("target",target)
	#cv2.waitKey()
	
	outcards = ''
	for key,value in cards.items():
		
		Template = cv2.imread(key+".png",cv2.IMREAD_GRAYSCALE)	#拼接数字模板文件
		x,Template = cv2.threshold(Template,230,255,cv2.THRESH_BINARY)	
		result = cv2.matchTemplate(target,Template,cv2.TM_SQDIFF_NORMED)

		numOfloc = 0
		loc = numpy.where(result<threshold)
		for other_loc in zip(*loc[::-1]):
			numOfloc = numOfloc + 1
			outcards += key
		cards[key] = cards[key] - numOfloc

	print('自家牌为：'+outcards)
	
def matchPiecesTemplate():
	target = cv2.imread(screenshotFile)
	Template = cv2.imread('0.png')
	
	up = target[205:235,775:795]
	left = target[590:620,130:150]
	down = target[980:1010,895:915]
	right = target[575:625,1525:1570]
	
	#hmerge=numpy.hstack((up,left,down,right))
	#cv2.imshow("target",hmerge)
	#cv2.waitKey()
	
	target_list=[0,up,left,down,right]
	for i in range(1,5):
		target = target_list[i]
		result = cv2.matchTemplate(target,Template,cv2.TM_SQDIFF_NORMED)
		loc = numpy.where(result<threshold)
		for other_loc in zip(*loc[::-1]):
			isZero[i]=1
	
def matchCardTemplate(position):
	matchPiecesTemplate()
	if position ==3 :
		pass
	else :
		if isZero[position] == 1:
			print("此家已无牌 跳过")
		else :
			target = cv2.imread(screenshotFile,cv2.IMREAD_GRAYSCALE)

			#up==1 left==2 down==3 right==4
			if position == 1:
				target=target[215:295,700:1000] #[上：下，左，右]
			elif position == 2:
				target=target[425:510,150:500] #left
			#elif position == 3:
			#	target=target[620:700,700:1000] #down
			elif position == 4:
				target=target[425:510,1200:1450] #right	
				
			x,target = cv2.threshold(target,230,255,cv2.THRESH_BINARY)	#230为红色扑克二值后与黑色扑克同识别
			
			outcards = ''
			for key,value in cards.items():
				Template = cv2.imread(key+".png",cv2.IMREAD_GRAYSCALE)	#拼接数字模板文件
				x,Template = cv2.threshold(Template,230,255,cv2.THRESH_BINARY)	
				
				result = cv2.matchTemplate(target,Template,cv2.TM_SQDIFF_NORMED)
				numOfloc = 0
				loc = numpy.where(result<threshold)
				for other_loc in zip(*loc[::-1]):
					numOfloc = numOfloc + 1
					outcards += key
				cards[key] = cards[key] - numOfloc

			print('出牌：' + outcards)
			
def matchClockTemplate():
	global out_order
	global restarted
	global cards	
	global isZero
	
	target = cv2.imread(screenshotFile)
	Template = cv2.imread('clock.png')
	mid = target[500:550,800:900]
	up = target[200:290,800:900]
	left = target[500:550,150:250] 
	down = target[650:750,800:900]
	right = target[500:550,1460:1550]


	result = cv2.matchTemplate(mid,Template,cv2.TM_SQDIFF_NORMED)
	loc = numpy.where(result<threshold)
	for other_loc in zip(*loc[::-1]):
		print("游戏重新开始中，重置记牌器")
		cards={'2':8,'3':8,'4':8,'5':8,'6':8,'7':8,'8':8,'9':8,'10':8,'J':8,'Q':8,'K':8,'A':8,'W':4}
		isZero=[0,0,0,0,0]
		restarted = True	

	target_list=[0,up,left,down,right]
	for i in range(1,5):
		target = target_list[i]
		result = cv2.matchTemplate(target,Template,cv2.TM_SQDIFF_NORMED)
		loc = numpy.where(result<threshold)
		for other_loc in zip(*loc[::-1]):
			if restarted == True :		
				matchSelfCards()	
				restarted = False						
				out_order = i						
				continue
				
			if out_order == i: 						
				continue			  
			
			if out_order < i:
				for times in range(out_order,i):
					matchCardTemplate(out_order)
					out_order += 1					
			elif out_order > i:
				for times in range(out_order,i+4):
					matchCardTemplate(out_order)
					out_order += 1
					if out_order > 4:
						out_order = out_order%4 

	
win = tkinter.Tk()
win.title('掼蛋网-记牌器	')
win.geometry('485x85')
var = tkinter.StringVar()
l = tkinter.Label(win, textvariable=var, bg='white', font=('Consolas',11,"bold"), width=500, height=5)
l.pack()
win.wm_attributes('-topmost',1)		

while(True):
	if(os.path.exists(screenshotFile)):		
		os.remove(screenshotFile)
		screenshot()
	else:
		screenshot()
	
	matchClockTemplate()
	x = prettytable.PrettyTable(list(cards.keys()))		#在gui上格式化输出列表
	x.add_row(list(cards.values()))
	var.set(x)
	win.update()
	time.sleep(1)

#hmerge=numpy.hstack((up,left,down,right))
#cv2.imshow("target",hmerge)
#cv2.waitKey()
#cv2.destroyAllWindows()
