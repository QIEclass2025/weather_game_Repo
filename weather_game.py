# 날씨 기반 업다운 게임 (Weather-Based Guessing Game)
# Weather API + Advice Slip API 활용

import tkinter as tk
from tkinter import messagebox, ttk
import requests
import random

class WeatherGuessingGame:
    """날씨 API를 활용한 업다운 게임"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ 날씨 기반 업다운 게임")
        self.root.geometry("600x700")
        self.root.configure(bg='#E3F2FD')
        
        # 게임 변수
        self.target_temp = 0
        self.attempts = 0
        self.max_attempts = 10
        self.game_active = False
        self.city_name = ""
        
        # UI 구성
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        # 타이틀
        title = tk.Label(self.root, text="🌤️ 날씨 기반 업다운 게임 🌤️",
                        font=('Arial', 20, 'bold'),
                        bg='#E3F2FD', fg='#1976D2')
        title.pack(pady=15)
        
        # 설명
        desc = tk.Label(self.root, 
                       text="실시간 날씨 데이터를 불러와 온도를 맞춰보세요!",
                       font=('Arial', 11),
                       bg='#E3F2FD', fg='#424242')
        desc.pack(pady=5)
        
        # 도시 선택 프레임
        city_frame = tk.LabelFrame(self.root, text="🌍 도시 선택",
                                   font=('Arial', 12, 'bold'),
                                   bg='#BBDEFB', padx=20, pady=15)
        city_frame.pack(pady=15, padx=20, fill='x')
        
        # 도시 목록 (위도, 경도)
        self.cities = {
            "서울": (37.5665, 126.9780),
            "부산": (35.1796, 129.0756),
            "뉴욕": (40.7128, -74.0060),
            "런던": (51.5074, -0.1278),
            "도쿄": (35.6762, 139.6503),
            "파리": (48.8566, 2.3522),
            "시드니": (-33.8688, 151.2093)
        }
        
        tk.Label(city_frame, text="도시를 선택하세요:",
                font=('Arial', 10), bg='#BBDEFB').pack()
        
        self.city_var = tk.StringVar(value="서울")
        city_menu = ttk.Combobox(city_frame, textvariable=self.city_var,
                                values=list(self.cities.keys()),
                                font=('Arial', 10), state='readonly', width=15)
        city_menu.pack(pady=5)
        
        # 날씨 정보 프레임
        weather_frame = tk.LabelFrame(self.root, text="☁️ 현재 날씨 정보",
                                     font=('Arial', 12, 'bold'),
                                     bg='#FFF9C4', padx=20, pady=15)
        weather_frame.pack(pady=10, padx=20, fill='x')
        
        self.weather_label = tk.Label(weather_frame,
                                      text="게임을 시작하여 날씨를 불러오세요!",
                                      font=('Arial', 10),
                                      bg='#FFF9C4', fg='#F57F17',
                                      wraplength=500, justify='left')
        self.weather_label.pack(pady=5)
        
        # 게임 정보 프레임
        info_frame = tk.LabelFrame(self.root, text="🎮 게임 정보",
                                  font=('Arial', 12, 'bold'),
                                  bg='#C8E6C9', padx=20, pady=15)
        info_frame.pack(pady=10, padx=20, fill='x')
        
        self.attempts_label = tk.Label(info_frame,
                                      text="시도 횟수: 0/10",
                                      font=('Arial', 11, 'bold'),
                                      bg='#C8E6C9', fg='#2E7D32')
        self.attempts_label.pack()
        
        self.hint_label = tk.Label(info_frame,
                                  text="범위: -30°C ~ 50°C",
                                  font=('Arial', 10),
                                  bg='#C8E6C9', fg='#424242')
        self.hint_label.pack(pady=5)
        
        # 입력 프레임
        input_frame = tk.Frame(self.root, bg='#E3F2FD')
        input_frame.pack(pady=15)
        
        tk.Label(input_frame, text="온도 입력 (°C):",
                font=('Arial', 11), bg='#E3F2FD').pack(side='left', padx=5)
        
        self.temp_entry = tk.Entry(input_frame, font=('Arial', 12), width=10)
        self.temp_entry.pack(side='left', padx=5)
        self.temp_entry.bind('<Return>', lambda e: self.check_guess())
        
        # 버튼 프레임
        button_frame = tk.Frame(self.root, bg='#E3F2FD')
        button_frame.pack(pady=10)
        
        self.start_btn = tk.Button(button_frame, text="🎮 게임 시작",
                                  command=self.start_game,
                                  font=('Arial', 11, 'bold'),
                                  bg='#4CAF50', fg='white',
                                  width=12, height=2)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.guess_btn = tk.Button(button_frame, text="🎯 온도 맞추기",
                                  command=self.check_guess,
                                  font=('Arial', 11, 'bold'),
                                  bg='#2196F3', fg='white',
                                  width=12, height=2,
                                  state='disabled')
        self.guess_btn.grid(row=0, column=1, padx=5)
        
        self.advice_btn = tk.Button(button_frame, text="💡 조언 받기",
                                   command=self.get_advice,
                                   font=('Arial', 11, 'bold'),
                                   bg='#FF9800', fg='white',
                                   width=12, height=2)
        self.advice_btn.grid(row=0, column=2, padx=5)
        
        # 조언 표시 프레임
        advice_frame = tk.LabelFrame(self.root, text="💭 오늘의 조언",
                                    font=('Arial', 11, 'bold'),
                                    bg='#F3E5F5', padx=15, pady=10)
        advice_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.advice_text = tk.Text(advice_frame, height=4, width=60,
                                  font=('Arial', 9), wrap='word',
                                  bg='#FCE4EC', fg='#880E4F',
                                  relief='flat')
        self.advice_text.pack(pady=5)
        self.advice_text.insert('1.0', "💡 '조언 받기' 버튼을 눌러 조언을 받아보세요!")
        self.advice_text.config(state='disabled')
        
    def fetch_weather(self, lat, lon):
        """Weather API에서 날씨 데이터 가져오기"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code",
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current']
                
                return {
                    'temperature': round(current['temperature_2m']),
                    'humidity': current['relative_humidity_2m'],
                    'weather_code': current['weather_code']
                }
            return None
        except Exception as e:
            messagebox.showerror("오류", f"날씨 정보를 불러올 수 없습니다: {str(e)}")
            return None
    
    def get_weather_description(self, code):
        """날씨 코드를 설명으로 변환"""
        weather_codes = {
            0: "맑음", 1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림",
            45: "안개", 48: "서리 안개",
            51: "이슬비", 53: "중간 이슬비", 55: "강한 이슬비",
            61: "약한 비", 63: "보통 비", 65: "강한 비",
            71: "약한 눈", 73: "보통 눈", 75: "강한 눈",
            80: "약한 소나기", 81: "보통 소나기", 82: "강한 소나기",
            95: "뇌우"
        }
        return weather_codes.get(code, "알 수 없음")
    
    def get_advice(self):
        """Advice Slip API에서 조언 가져오기"""
        try:
            response = requests.get("https://api.adviceslip.com/advice", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                advice = data['slip']['advice']
                
                self.advice_text.config(state='normal')
                self.advice_text.delete('1.0', 'end')
                self.advice_text.insert('1.0', f"💡 {advice}")
                self.advice_text.config(state='disabled')
            else:
                messagebox.showwarning("알림", "조언을 불러올 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"조언 API 오류: {str(e)}")
    
    def start_game(self):
        """게임 시작"""
        city = self.city_var.get()
        self.city_name = city
        lat, lon = self.cities[city]
        
        # 날씨 정보 가져오기
        weather = self.fetch_weather(lat, lon)
        
        if weather is None:
            return
        
        self.target_temp = weather['temperature']
        weather_desc = self.get_weather_description(weather['weather_code'])
        
        # 날씨 정보 표시
        weather_info = (f"🌍 도시: {city}\n"
                       f"🌡️ 현재 날씨: {weather_desc}\n"
                       f"💧 습도: {weather['humidity']}%\n"
                       f"❓ 현재 온도를 맞춰보세요!")
        
        self.weather_label.config(text=weather_info)
        
        # 게임 초기화
        self.attempts = 0
        self.game_active = True
        self.update_attempts()
        self.hint_label.config(text="범위: -30°C ~ 50°C")
        
        # 버튼 상태 변경
        self.start_btn.config(state='disabled')
        self.guess_btn.config(state='normal')
        self.temp_entry.delete(0, 'end')
        self.temp_entry.focus()
        
        messagebox.showinfo("게임 시작", 
                          f"{city}의 현재 온도를 맞춰보세요!\n"
                          f"10번의 기회가 있습니다.")
    
    def update_attempts(self):
        """시도 횟수 업데이트"""
        self.attempts_label.config(text=f"시도 횟수: {self.attempts}/{self.max_attempts}")
    
    def check_guess(self):
        """추측 확인"""
        if not self.game_active:
            messagebox.showwarning("알림", "먼저 게임을 시작하세요!")
            return
        
        try:
            guess = int(self.temp_entry.get())
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력하세요!")
            return
        
        self.attempts += 1
        self.update_attempts()
        
        diff = abs(self.target_temp - guess)
        
        # 정답 확인
        if guess == self.target_temp:
            self.game_active = False
            self.guess_btn.config(state='disabled')
            self.start_btn.config(state='normal')
            
            messagebox.showinfo("축하합니다! 🎉",
                              f"정답입니다!\n\n"
                              f"온도: {self.target_temp}°C\n"
                              f"시도 횟수: {self.attempts}회")
            return
        
        # 힌트 제공
        if diff <= 2:
            hint = "🔥 매우 뜨겁습니다! (±2°C 이내)"
        elif diff <= 5:
            hint = "♨️ 뜨겁습니다! (±5°C 이내)"
        elif diff <= 10:
            hint = "🌡️ 따뜻합니다! (±10°C 이내)"
        else:
            hint = "❄️ 차갑습니다! (±10°C 이상)"
        
        if guess < self.target_temp:
            direction = "⬆️ UP! 더 높은 온도입니다."
        else:
            direction = "⬇️ DOWN! 더 낮은 온도입니다."
        
        self.hint_label.config(text=f"{hint}\n{direction}")
        
        # 시도 횟수 초과
        if self.attempts >= self.max_attempts:
            self.game_active = False
            self.guess_btn.config(state='disabled')
            self.start_btn.config(state='normal')
            
            messagebox.showinfo("게임 종료",
                              f"시도 횟수를 모두 사용했습니다.\n\n"
                              f"정답: {self.target_temp}°C\n"
                              f"{self.city_name}의 현재 온도였습니다.")
        
        self.temp_entry.delete(0, 'end')
        self.temp_entry.focus()

# 게임 실행
if __name__ == "__main__":
    root = tk.Tk()
    game = WeatherGuessingGame(root)
    root.mainloop()
