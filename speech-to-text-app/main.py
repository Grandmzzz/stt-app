import pyaudio
import threading
import os
import wave
import tkinter as tk
import speech_recognition as sr


# Объект записи ауидо
class VoiceRecorder():
    def __init__(self):
        self.recording = False
        self.audio = pyaudio.PyAudio()

    def get_recording_status(self):
        return self.recording

    def record_handler(self):
        if self.recording:
            self.recording = False
        else:
            self.recording = True
            threading.Thread(target=self.record).start()

    def record(self):
        stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100,
                                 input=True, frames_per_buffer=1024)

        frames = []

        while self.recording:
            data = stream.read(1024)
            frames.append(data)
            # мб добавить таймер
        stream.stop_stream()
        stream.close()

        if os.path.exists("record.wav"):
            os.remove("record.wav")

        record_file = wave.open("record.wav", "wb")
        record_file.setnchannels(1)
        record_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        record_file.setframerate(44100)
        record_file.writeframes(b"".join(frames))
        record_file.close()


# Объект распознавателя голоса
class VoiceRecogniser:
    def __init__(self, audio_name):
        self.r = sr.Recognizer()
        exist_flag = False
        while not exist_flag:
            try:
                recording = sr.AudioFile(audio_name)
                with recording as source:
                    self.audio = self.r.record(source)
            except FileNotFoundError:
                pass
            except ValueError:
                pass
            else:
                exist_flag = True

    def recognize_audio(self):
        try:
            text = self.r.recognize_google(self.audio, language="ru-RU")
        except sr.exceptions.UnknownValueError:
            raise ValueError
        else:
            return text


# Вывод данных в текстовое поле
def print_textbox(text_box, message):
    text_box.delete('1.0', tk.END)
    text_box.insert(1.0, message)
    message = str()


# Хендлер кнопки записи звука
def record_handle(recorder, msg_text_box):
    recorder.record_handler()
    if recorder.get_recording_status():
        print_textbox(msg_text_box, 'Запись начата')
    else:
        output = 'Запись завершена\n'
        r = VoiceRecogniser('record.wav')
        try:
            text = r.recognize_audio()
        except ValueError:
            output += 'Некорректное произношение, запишите звук заново'
        else:
            output += 'Вы сказали: \n"'
            output += text + '"'
        print_textbox(msg_text_box, output)
        os.remove("record.wav")


if __name__ == '__main__':
    # Главное окно
    window = tk.Tk()
    window.geometry('300x500')
    window.title('Speech To Text')

    frame = tk.LabelFrame(master=window)
    frame.pack(padx=0.5, pady=0.5, anchor=tk.CENTER)

    # Текстовое поле с уведомлениями о записи
    msg_text_box = tk.Text(width=34, height=25, master=frame, wrap=tk.WORD)
    msg_text_box.grid(column=0, row=0, padx=5, pady=5)

    # Фрейм с кнопками
    frame_buttons = tk.Frame(master=frame)
    frame_buttons.grid(column=0, row=1, padx=5, pady=5)

    # Объект записывателя
    recorder = VoiceRecorder()
    # Кнопка записи звука
    btn_record = tk.Button(master=frame_buttons, height=1, width=7, text='record!',
                        command=lambda: record_handle(recorder, msg_text_box))
    btn_record.grid(column=0, row=0, padx=5, pady=5)


    frame.mainloop()
    window.mainloop()

