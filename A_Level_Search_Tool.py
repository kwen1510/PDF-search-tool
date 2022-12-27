import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
import os
import webbrowser
import os.path
import re
import json
import PyPDF2 
from PyPDF2 import PdfFileReader
from subprocess import call
import glob
import fitz
import subprocess

### Imported functions ###

def open_PDF_to_specific_page():

	page_number = page_finder.get()

	if not page_number:
		output.delete(1.0,END)
		output.insert(END, "Please key in a page number." + '\n')
		print("Nothing found!")
		return

	try:
		path_to_pdf = get_file_name()
	except:
		# Move back by one page
		os.chdir("../")
		path_to_pdf = get_file_name()

	# I am testing this on my Windows Install machine

	adobe_file_path = get_adobe_exe_path()

	path_to_acrobat = os.path.abspath(adobe_file_path) 

	print(f'Opening page {page_number}...')
	# this will open your document on page 12
	process = subprocess.Popen([path_to_acrobat, '/A', f'page={page_number}', path_to_pdf], shell=False, stdout=subprocess.PIPE)
	# process.wait()


def get_bookmarks_json():

    # Get file directory

    current_dir = os.getcwd()

    folder_name = "Extracted Text Files"

    pdf_file_name = get_file_name()

    pdf_file_path = current_dir + "\\" + pdf_file_name

    bookmark = ''
    try:
        doc = fitz.open(pdf_file_path) 
        toc = doc.getToC(simple = True)
        # print(type(toc))
        # print(toc)

        bookmark_array = []
        for bookmarks in toc:
            bookmark_array.append(bookmarks[1:3])

        # print(bookmark_array)

    except Exception as e:
        print(e)

    bookmark_pages = dict() 
    for bookmark_sets in bookmark_array:
      bookmark_pages[bookmark_sets[1]] = bookmark_sets[0]

    # print(bookmark_pages)


    # Remove non-20xx bookmarks from list

    to_delete = []

    for k, v in bookmark_pages.items():
        if v[:2] != '20':
            to_delete.append(k)

    # print(to_delete)

    for remove_page in to_delete:
        bookmark_pages.pop(remove_page)

    print(bookmark_pages)

    with open(f'{folder_name}/bookmarks.json', 'w', encoding="utf-8") as f:
        json.dump(bookmark_pages, f)
        f.close()


def get_file_name():
	#open text file in read mode
	text_file = open("FileName.txt", "r")

	#read whole file to a string
	file_name = text_file.readline()

	#close file
	text_file.close()

	return file_name

def get_adobe_exe_path():
	#open text file in read mode
	pdf_exe_file = open("AcrobatPath.txt", "r")

	#read whole file to a string
	pdf_exe_path = pdf_exe_file.readline()

	#close file
	pdf_exe_file.close()

	return pdf_exe_path

# Extract all texts to file
def extract():

	current_dir = os.getcwd()

	folder_name = "Extracted Text Files"

	files = glob.glob(f'{folder_name}/*')
	for f in files:
	    os.remove(f)

	# pdf_file_name = "A level Papers 2003-2021.pdf"
	# pdf_file_name = "Example.pdf"

	print(current_dir)

	pdf_file_name = get_file_name()

	pdf_file_path = current_dir + "\\" + pdf_file_name

	# print(pdf_file_path)

	# creating a pdf file object
	pdfFileObject = open(pdf_file_path, 'rb')

	pdfReader = PyPDF2.PdfFileReader(pdfFileObject)

	for i in range(0,pdfReader.numPages):

		with open(f'{folder_name}/page_{i+1}.txt', 'w', encoding="utf-8") as f:

		    # creating a page object
		    pageObj = pdfReader.getPage(i)

		    # extracting text from page
		    text = pageObj.extractText()

		    f.write(text)

		    f.close()

	# Run bookmarks to text file function
	get_bookmarks_json()


	return

def search_keyword(keyword, current_path):

	os.chdir(current_path)

	current_dir = os.getcwd()
	# print(current_dir)

	folder_name = "Extracted Text Files"


	list = os.listdir(folder_name)
	number_of_files = len(list)
	# print(number_of_files)

	os.chdir(f'{folder_name}')
	current_dir = os.getcwd()

	# Get all bookmarks
	with open('bookmarks.json') as json_file:
		bookmark_pages = json.load(json_file)

	#Create an array to store the text
	extracted_sentences = []


	#Loop through all files
	for i in range(0,number_of_files-1):

		with open(f'page_{i+1}.txt', encoding="UTF-8") as f:
			contents = f.read()
			# print(f"Page {i+1}")
			# print(contents)
			# print("\n\n\n")

			#Search within text
			sentences = re.findall(rf"([^.]*?{keyword.lower()}[^.]*\.)",contents.lower())

			if sentences:
				# print(sentences)

				# Get current page
				current_page = i+1

				# print(current_page)

				if bookmark_pages:

					for page_number in bookmark_pages:
					    if int(page_number) <= current_page:
					        lowest_page = int(page_number)
					    else:
					        break
					        
					# print(lowest_page)

					current_paper = bookmark_pages[str(lowest_page)]

					current_page_in_paper = current_page - lowest_page + 1

					output_line = f'({current_paper}, Page {current_page_in_paper})'

				else:
					output_line = ""

				# print(output_line)

				#Append page number to all elements in array
				sentences_mapped = [f'Page {i+1} {output_line}: ' + s for s in sentences]

				# print(sentences_mapped)
				sentences_mapped = "\n\n".join(sentences_mapped)

				#If text exists, push into array with "Page number: " appended to back
				extracted_sentences.append(sentences_mapped) 

	#Join all strings together with line breaks
	# print(extracted_sentences)

	# extracted_sentences = extracted_sentences.flip()

	full_text = "\n\n".join(extracted_sentences)

	# print(full_text)

	return full_text




file_name = get_file_name()

# Get current directory
current_dir = os.getcwd()

gui = tk.Tk()
#getting screen width and height of display
width= gui.winfo_screenwidth() 
height= gui.winfo_screenheight()
#setting tkinter window size
gui.geometry("%dx%d" % (width, height))
Label(gui, text="Search in TYS").pack()


def hit_enter(e):
	getEntry()

# Define all functions
def getEntry():

	# # Clear previous output
	# loading.delete(1.0,END)

	# loading.insert(END, "Searching... \nThe file is huge... \n18 years worth of stuff...")
	# time.sleep(0.1)

	# Search for keyword
	keyword = myEntry.get()

	# Exit if blank
	if keyword == "":
		output.insert(END, "Please key something in." + '\n')
		return


	found_sentences = search_keyword(keyword,current_dir)

	# Create output
	if not found_sentences:
    # Clear previous output
		output.delete(1.0,END)
		output.insert(END, "Nothing Found." + '\n')
		print("Nothing found!")


	else:
	# Clear previous output
		output.delete(1.0,END)

    	# Loop through all
		for sentence in found_sentences:
			output.insert(END, sentence)


def open_PDF():
	# Open up PDF file
	webbrowser.open_new(rf'{current_dir}/{file_name}')

def prep_document():
	# Open up PDF file
	extract()
	output.delete(1.0,END)
	output.insert(END, "PDF contents extracted!" + '\n')


# Create UI stuff

title = tk.Label(text="Keyword:")
title.pack()

myEntry = tk.Entry(gui, width=40)
myEntry.config(font=('Arial',20))
myEntry.pack(pady=20)

btn1 = tk.Button(gui, height=1, width=20, text="Extract from PDF", command=prep_document, bg='#ffffed')
btn1.pack(pady=0)

btn2 = tk.Button(gui, height=1, width=10, text="Open PDF", command=open_PDF, bg='#90EE90')
btn2.pack(pady=5)

btn3 = tk.Button(gui, height=1, width=10, text="Find", command=getEntry, bg='#ADD8E6')
btn3.pack(pady=0)

page_finder = tk.Entry(gui, width=7)
page_finder.config(font=('Arial',20))
page_finder.pack(pady=5)

btn4 = tk.Button(gui, height=1, width=20, text="Open Specific Page", command=open_PDF_to_specific_page, bg='#D4F0F0')
btn4.pack(pady=0)

# title = tk.Label(text="Status:")
# title.pack()

# loading = Text(gui, width=40, height=1)
# loading.insert(END, "Please type in a keyword above")
# loading.pack(pady = 20)

# Create scrollbar
output = scrolledtext.ScrolledText(gui, undo=True)
output.config(font=('Arial',12))
output.pack(expand=True, fill='both', pady=20, padx=20)


gui.bind('<Return>',hit_enter)







# Start loop

gui.mainloop()

'''
Source: 
- https://realpython.com/python-gui-tkinter/
- https://stackhowto.com/how-to-get-value-from-entry-on-button-click-in-tkinter/

'''