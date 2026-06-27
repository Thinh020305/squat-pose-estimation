# Squat Pose Estimation

## README - Huong dan cai dat va chay ung dung

Du an **Squat Pose Estimation** xay dung he thong nhan dien, dem so lan va danh gia tu the squat cua nguoi dung thong qua webcam. He thong su dung **OpenCV** de lay hinh anh tu camera, **MediaPipe Pose** de nhan dien cac diem khop tren co the, ket hop voi cac cong thuc tinh goc va mo hinh hoc may de cham diem, dua ra phan hoi va luu lich su tap luyen.

---

## Muc luc

1. Tong quan du an
2. Chuc nang chinh
3. Cau truc thu muc
4. Yeu cau he thong
5. Cai dat moi truong Python
6. Cai dat thu vien
7. Chay ung dung web
8. Tai khoan, lich su va tien trinh tap luyen
9. Huan luyen mo hinh AI
10. Luu y ve file khong dua len GitHub
11. Loi thuong gap

---

## 1. Tong quan du an

He thong ho tro nguoi dung tap squat bang cach phan tich tu the theo thoi gian thuc. Khi nguoi dung bat dau buoi tap, webcam se ghi hinh, MediaPipe Pose se nhan dien cac landmark tren co the nhu vai, hong, dau goi, co chan va ban chan. Tu cac landmark nay, he thong tinh toan cac thong so quan trong nhu goc goi, do nghieng than nguoi va thoi gian thuc hien moi lan squat.

Sau moi lan squat hop le, chuong trinh se:

- Dem so lan squat.
- Cham diem dong tac.
- Dua ra phan hoi ky thuat.
- Luu ket qua vao co so du lieu.
- Hien thi lich su va tien trinh cai thien cua nguoi dung.

Ung dung duoc xay dung theo mo hinh Flask MVC, gom cac phan controller, model, service va giao dien web.

---

## 2. Chuc nang chinh

- Dang ky va dang nhap tai khoan nguoi dung.
- Mo webcam va nhan dien tu the squat theo thoi gian thuc.
- Ve khung xuong co the bang MediaPipe Pose.
- Tinh goc goi, do nghieng than nguoi va thoi gian thuc hien rep.
- Dem so lan squat hop le.
- Cham diem tung rep dua tren do sau, than nguoi va nhip do.
- Phan loai mot so loi squat bang mo hinh hoc may.
- Luu lich su buoi tap va diem tung rep.
- Hien thi bieu do tien trinh cai thien theo score.
- Quan tri vien co the huan luyen lai mo hinh SVM hoac Random Forest.

---

## 3. Cau truc thu muc

```text
Squat_pose_estimation/
|
|-- app.py                         # File khoi chay Flask app
|-- main.py                        # File tien ich chay app va mo trinh duyet
|-- wsgi.py                        # Entry point cho WSGI server
|-- requirements.txt               # Danh sach thu vien can cai
|-- README.md                      # Tai lieu huong dan du an
|
|-- backend/
|   |-- controllers/               # Xu ly route va request Flask
|   |   |-- auth_controller.py
|   |   |-- pose_controller.py
|   |   `-- workout_controller.py
|   |
|   |-- models/                    # Lam viec voi database
|   |   |-- user_model.py
|   |   |-- workout_model.py
|   |   `-- result_model.py
|   |
|   |-- services/                  # Xu ly logic chinh cua he thong
|   |   |-- pose_service.py         # Nhan dien pose, webcam, landmark
|   |   |-- angle_service.py        # Tinh goc co the
|   |   |-- squat_counter_service.py# Dem rep squat
|   |   |-- feedback_service.py     # Cham diem rule-based
|   |   |-- ml_service.py           # ML classifier
|   |   |-- train_svm.py            # Train SVM
|   |   `-- train_random_forest.py  # Train Random Forest
|   |
|   |-- database/
|   |   `-- db.py                   # Khoi tao SQLite schema
|   |
|   `-- utils/
|
|-- frontend/
|   |-- templates/                 # HTML templates
|   |-- static/                    # CSS, JavaScript
|   `-- uploads/
|
|-- data/
|   `-- squat_features_augmented.csv
|
`-- ml_models/                     # Mo hinh .pkl neu duoc train rieng
```

---

## 4. Yeu cau he thong

- He dieu hanh: Windows 10/11, macOS hoac Linux.
- Python: **3.10 tro xuong** de dam bao tuong thich voi MediaPipe.
- Webcam hoat dong binh thuong.
- Trinh duyet: Chrome, Edge, Firefox hoac cac trinh duyet hien dai.
- Ket noi Internet khi cai thu vien lan dau.

Kiem tra phien ban Python:

```powershell
python --version
```

Phien ban khuyen nghi:

```text
Python 3.10.x
```

---

## 5. Cai dat moi truong Python

Sau khi tai project ve may, mo thu muc project bang Visual Studio Code, sau do mo terminal tai thu muc goc cua project.

Vi du thu muc project:

```powershell
cd C:\Users\Admin\Documents\Squat_pose_estimation
```

Tao moi truong ao `.venv`:

```powershell
python -m venv .venv
```

Kich hoat moi truong ao tren Windows PowerShell:

```powershell
.\.venv\Scripts\activate
```

Neu kich hoat thanh cong, terminal se co dang:

```powershell
(.venv) PS C:\Users\Admin\Documents\Squat_pose_estimation>
```

Neu dung Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

Neu dung macOS/Linux:

```bash
source .venv/bin/activate
```

Thoat moi truong ao khi can:

```powershell
deactivate
```

---

## 6. Cai dat thu vien

Sau khi da kich hoat `.venv`, cai dat cac thu vien can thiet bang file `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Cac thu vien chinh trong project:

```text
mediapipe
opencv-python
numpy
pandas
scikit-learn
joblib
Flask
```

Co the cai thu cong tung thu vien neu can:

```powershell
pip install mediapipe==0.10.14
pip install opencv-python
pip install numpy
pip install pandas
pip install scikit-learn
pip install joblib
pip install Flask
```

Kiem tra nhanh cac thu vien da cai thanh cong:

```powershell
python -c "import flask, cv2, mediapipe, pandas, sklearn, joblib; print('OK')"
```

Neu in ra `OK` la moi truong da san sang.

---

## 7. Chay ung dung web

Chay ung dung Flask:

```powershell
python app.py
```

Hoac chay bang Python trong `.venv`:

```powershell
.\.venv\Scripts\python.exe app.py
```

Ket qua mong doi tren terminal:

```text
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

Mo trinh duyet va truy cap:

```text
http://127.0.0.1:5000
```

Dung server:

```text
Nhan Ctrl + C trong terminal dang chay Flask
```

---

## 8. Tai khoan, lich su va tien trinh tap luyen

Sau khi chay web app, nguoi dung co the:

1. Dang ky tai khoan moi.
2. Dang nhap vao he thong.
3. Vao trang Dashboard de xem tong quan.
4. Chon chuc nang tap voi webcam.
5. Thuc hien squat truoc camera.
6. Xem so rep, score va feedback.
7. Xem lich su buoi tap va bieu do tien trinh cai thien.

Du lieu runtime duoc luu trong SQLite. File database se duoc tao tu dong neu chua co.

---

## 9. Huan luyen mo hinh AI

Project co 2 script huan luyen mo hinh:

### Train SVM

```powershell
python -m backend.services.train_svm
```

Mo hinh dau ra:

```text
ml_models/squat_error_model.pkl
```

### Train Random Forest

```powershell
python -m backend.services.train_random_forest
```

Mo hinh dau ra:

```text
ml_models/squat_random_forest_model.pkl
```

Dataset su dung:

```text
data/squat_features_augmented.csv
```

Khi chay ung dung, he thong uu tien dung Random Forest neu co file model. Neu khong co model, he thong se fallback ve cach cham diem rule-based.

---

## 10. Luu y ve file khong dua len GitHub

Khong nen dua cac file sau len GitHub:

```text
.venv/
.idea/
__pycache__/
*.pyc
*.sqlite3
ml_models/*.pkl
```

Ly do:

- `.venv/` chua thu vien cai dat tren may local, dung luong lon va khong can thiet.
- `__pycache__/`, `*.pyc` la file cache Python.
- `*.sqlite3` la database runtime, co the chua du lieu local.
- `*.pkl` co the rat nang, de vuot gioi han GitHub.

Nguoi khac tai project ve chi can tao lai `.venv` va cai thu vien bang:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 11. Loi thuong gap

### Loi 1: Khong tim thay Flask hoac MediaPipe

Thong bao loi co dang:

```text
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'mediapipe'
```

Cach sua:

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Loi 2: Khong mo duoc webcam

Nguyen nhan co the do:

- Webcam dang duoc ung dung khac su dung.
- Trinh duyet/he dieu hanh chua cap quyen camera.
- May tinh khong co camera hoac camera bi loi driver.

Cach xu ly:

- Tat cac ung dung dang dung camera.
- Kiem tra quyen camera trong Windows Settings.
- Thu chay lai ung dung.

### Loi 3: Port 5000 da duoc su dung

Thong bao co the gap:

```text
Address already in use
Port 5000 is in use
```

Kiem tra tien trinh dang dung port 5000:

```powershell
netstat -ano | Select-String ':5000'
```

Dung tien trinh theo PID:

```powershell
Stop-Process -Id <PID>
```

Sau do chay lai:

```powershell
python app.py
```

### Loi 4: MediaPipe khong cai duoc

Can dam bao dang dung Python 3.10 tro xuong:

```powershell
python --version
```

Neu dang dung Python qua moi, hay cai Python 3.10 va tao lai `.venv`.

### Loi 5: GitHub hien qua nhieu file trong `.venv`

Nguyen nhan la `.venv` da bi Git track truoc do. Cach xu ly:

```powershell
git rm -r --cached .venv
git add .gitignore
git commit -m "Remove local environment from repository"
git push
```

Luu y: lenh tren khong xoa `.venv` tren may local, chi xoa khoi Git tracking.

---

## Tom tat lenh cai dat nhanh tren Windows

```powershell
cd C:\Users\Admin\Documents\Squat_pose_estimation
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Sau do mo:

```text
http://127.0.0.1:5000
```
