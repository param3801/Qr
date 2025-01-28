from django.shortcuts import render,redirect
import qrcode
from scanner.models import QRcode
from django.core.files.storage import FileSystemStorage
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
from django.http import HttpResponseRedirect

from PIL import Image
from pyzbar.pyzbar import decode




def generate_qr(request):
  qr_image_url=None
  if request.method =='POST':
    mobile_number=request.POST.get('mobile')
    data=request.POST.get('textField')
    if not mobile_number or len(mobile_number) != 10 :
      return render(request,'scanner/generate.html',{'error':'Invalid mobile number !'})
    
    
    qr_content= f"{mobile_number}|{data}"
    qr = qrcode.make(qr_content)
    qr_image_io = BytesIO()  #create a Byteiios stream
    qr.save(qr_image_io,format='PNG')  #Save the qrcode at that location
    qr_image_io.seek(0)  #Restart the position of the stream

    #Define the storage location of the qr code image

    storage_qr = settings.MEDIA_ROOT / 'qr_codes'
    fs = FileSystemStorage(location=storage_qr ,base_url='/media/qr_codes/')
    filename = f"{data}_{mobile_number}.png"
    qr_image_content=ContentFile(qr_image_io.read(),name=filename)
    file_path=fs.save(filename,qr_image_content)
    qr_image_url=fs.url(filename)
    QRcode.objects.create(mobile_number=mobile_number,data=data)
   
  else:
    qr_image_url=None

  return render(request,'scanner/generate.html',{'qr_image_url':qr_image_url})
  
 

def scan_qr(request):
  result  = ''
  if request.method == 'POST' and request.FILES.get('image'):
    mobile_number= request.POST['mobile']
    qr_image = request.FILES.get('image')
    if not mobile_number or len(mobile_number) != 10:
      return render(request,'scanner/scan.html',{'error':'Invalid mobile number !'})
    
    #save the upload image
    fs = FileSystemStorage()
    filename=fs.save(qr_image.name , qr_image)
    image_path = Path(fs.location) / filename

    try:
      #Open the image and decode it
      image = Image.open(image_path)
      decoded_objects = decode(image)

      if decoded_objects:
        #get the data from first decoded objects
        qr_content = decoded_objects[0].data.decode('utf-8').strip()
        qr_mobile_number ,qr_data  = qr_content.split('|')

        #Check if the data in the QR code if same the the previous ones

        qr_entry = QRcode.objects.filter(data = qr_data, mobile_number = qr_mobile_number).first()
        if qr_entry and mobile_number==qr_mobile_number:
          result = ' Scan:Success valid QR for the provided mobile number'

          #delete the specific QR code from database
          qr_entry.delete()
          #delete the image from media/qr_codes
          qr_image_path = settings.MEDIA_ROOT / 'qr_codes' / f"{qr_data}_{qr_mobile_number}.png"
          if qr_image_path.exists():
            qr_image_path.unlink()

          #delete the  uploaded image from media
          if image_path.exists():
            image_path.unlink() 
        else:
          result = 'Scan:Failed Invalid QR code for the provided mobile number'
      else:
        result = "No QR code is detected in image."   

    except Exception as e:
      result = f"Error processing the image {str(e)}"

    finally: 
      # insure the provided image remove regardless of result.
      if image_path.exists():
        image_path.unlink()
    
    return render(request,'scanner/scan.html',{'result':result})
  
  
  return render(request,'scanner/scan.html')