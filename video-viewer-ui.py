import cv2
import requests
import numpy as np
import threading
from tkinter import Tk, Label, Entry, Button, Listbox, messagebox

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ESP32-CAM IP adreslerini tutan bir liste
esp32_urls = []
streaming = False  
face_detection_active = False  

# Video akışını başlatan fonksiyon
def stream_video(url, window_name, detect_faces=False):
    global streaming, face_detection_active
    try:
        stream = requests.get(url, stream=True, timeout=5)
        if stream.status_code == 200:
            bytes_data = b""
            streaming = True
            for chunk in stream.iter_content(chunk_size=1024):
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8')  # JPEG başlangıcı
                b = bytes_data.find(b'\xff\xd9')  # JPEG sonu
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        if detect_faces or face_detection_active:  
                            detect_and_display_faces(frame, window_name)
                        else:
                            cv2.imshow(window_name, frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        else:
            messagebox.showerror("Bağlantı Hatası", f"Bağlanılamadı: {stream.status_code} - {url}")
    except Exception as e:
        messagebox.showerror("Bağlantı Hatası", f"Bağlantı sırasında hata oluştu: {str(e)}")
    finally:
        streaming = False
        cv2.destroyWindow(window_name)

# Yüz tespiti yapan fonksiyon
def detect_and_display_faces(frame, window_name):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
    cv2.imshow(window_name, frame)

# Cihaz ekleme fonksiyonu
def add_device():
    ip_address = ip_entry.get().strip()
    
    if not ip_address:
        messagebox.showwarning("Hata", "Lütfen bir IP adresi girin.")
        return
    
    
    if not ip_address.startswith("192.168."):
        ip_address = f"192.168.1.{ip_address}"
    
    # URL oluştur ve listeye ekle
    url = f"http://{ip_address}:81/stream"
    esp32_urls.append(url)
    device_listbox.insert("end", ip_address)
    ip_entry.delete(0, "end")


# Video izleme fonksiyonu
def view_video():
    global face_detection_active
    selected_index = device_listbox.curselection()
    if not selected_index:
        messagebox.showwarning("Hata", "Lütfen bir cihaz seçin.")
        return
    ip_address = device_listbox.get(selected_index)
    url = f"http://{ip_address}:81/stream"
    threading.Thread(target=stream_video, args=(url, f"ESP32-CAM {ip_address}", False)).start()
    face_detection_active = False  # Video izleme başlarken yüz tespiti durdurulsun

# Yüz tespiti özelliğini başlatma fonksiyonu
def start_face_detection():
    global face_detection_active
    if not streaming:
        messagebox.showwarning("Hata", "Önce video akışını başlatmalısınız.")
        return
    if not face_detection_active:
        face_detection_active = True
        messagebox.showinfo("Bilgi", "Yüz tespiti başlatıldı.")
    else:
        messagebox.showinfo("Bilgi", "Yüz tespiti zaten aktif.")

# Ana uygulama penceresi
root = Tk()
root.title("ESP32-CAM İzleme ve Yüz Tespiti")
root.geometry("400x400")

# Kullanıcı arayüzü bileşenleri
Label(root, text="ESP32-CAM Cihaz Ekle").pack(pady=10)

ip_entry = Entry(root, width=30)
ip_entry.pack(pady=5)

add_button = Button(root, text="Cihaz Ekle", command=add_device)
add_button.pack(pady=5)

Label(root, text="Cihaz Listesi").pack(pady=10)

device_listbox = Listbox(root, width=40, height=10)
device_listbox.pack(pady=5)

view_button = Button(root, text="Video İzle", command=view_video)
view_button.pack(pady=5)

face_button = Button(root, text="Face Detect", command=start_face_detection)
face_button.pack(pady=5)

# Uygulamayı çalıştır
root.mainloop()
