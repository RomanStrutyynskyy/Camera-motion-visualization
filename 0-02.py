import subprocess
import numpy as np
from vidstab import VidStab
from PIL import Image, ImageDraw
import os.path
import time

def make_list():
    "make list of files"

    patdir = os.getcwd()
    print ('Working direktory', patdir)
    list_vid_files = open('0-01 LIST-OF-{}.log'.format(videofile_ext), 'w')
    for file in os.listdir(patdir):
        if file.endswith(videofile_ext):
            print(os.path.join(file))
            list_vid_files.write(os.path.join(file))
            list_vid_files.write('\n')
    list_vid_files.close()
    with open('0-01 LIST-OF-{}.log'.format(videofile_ext)) as file:
        global num_vid_files
        num_vid_files = [row.strip() for row in file]
    print (len(num_vid_files), 'файлів')
    print ('++++++++++++++++++')


def analiz_video():
    "Analizing videfile"

    for n in range (0, len(num_vid_files)):
        start = time.time()
        video_file_prefix = num_vid_files[n].replace(videofile_ext, '')
        video_file_name = video_file_prefix + videofile_ext
        text_file_name = video_file_prefix + '.txt'
        #аналізуємо відкритий файл на предмет переміщень камери
        try:
            stabilizer = VidStab()
            stabilizer.gen_transforms(video_file_name)
        except Exception:
            print ('#', n+1, 'from ', len(num_vid_files),' ','ERROR')
            error_analiz = open(text_file_name, 'w')
            error_log = open('0-01 ELOG.log', 'a')
            for zapyz in range (0, 100):
                error_analiz.write('0.01e+00,0.01e+99,0.01e+00\n')
            error_log.write(text_file_name)
            error_log.write('\n')
            error_analiz.close()
            error_log.close()
            continue
        #отриманий результат записуємо в файл "назва відео.тхт"
        np.savetxt(text_file_name, stabilizer.transforms, delimiter=',')
        with open(text_file_name) as file:
            finish = time.time()
            nframes = [row.strip() for row in file]
        duration = ('{:02d}:{:02d}:{:02d}'.format(len(nframes) // 1500,
                                                  (len(nframes) - (len(nframes) // 1500) * 1500) // 25,
                                                  len(nframes) % 25 + 1))
        print ('{:3d} / {:3d}  {} || {:5d} frames, duration {}  {:.3f} seconds in processing'.format(n + 1,
                                                                                          len(num_vid_files),
                                                                                          num_vid_files[n],
                                                                                          len(nframes), duration,
                                                                                          (finish - start)))
def make_image():
    "Build visualization camera movement"
    with open('0-01 LIST-OF-{}.log'.format(videofile_ext)) as file:
        num_vid_files = [row.strip() for row in file]
    for n in range (0, len(num_vid_files)):
        video_file = num_vid_files[n].replace(videofile_ext, '.txt')
        result_image = num_vid_files[n].replace(videofile_ext, '.png')
    #----------
        with open(video_file) as file:
            num_of_frames = [row.strip() for row in file]
        scr_x = len(num_of_frames)
        scr_y = 21
        img = Image.new('RGB', (scr_x + 1, scr_y + 1), 'black')
        draw = ImageDraw.Draw(img)
        canvas_pixels = img.load()
        for i in range(0, len(num_of_frames)):
            triada = num_of_frames[i].split(',')
            pan = int(round(abs((float(triada[0]) * 2.6))))
            scan = int(round(abs((float(triada[1]) * 2.6))))
            rot = int(round(abs((float(triada[2]) * 1600))))
            if pan > 254:
                pan = 254
            if scan > 254:
                scan = 254
            if rot > 254:
                rot = 254
            draw.line(((i, 0), (i, 4)), fill=(0, pan, 0), width=1)
            draw.line(((i, 5), (i, 9)), fill=(scan, 0, 0), width=1)
            draw.line(((i, 10), (i, 14)), fill=(0, 0, rot), width=1)
            draw.line(((i, 15), (i, 21)), fill=(scan, pan, rot), width=1)
            if i%25 == 0:
                draw.line(((i, 0), (i, 4)), fill=(254, 254, 254), width=1)
            if i%(25*10) == 0:
                draw.line(((i, 0), (i, 14)), fill=(254, 254, 254), width=2)
            if i%(25*60) == 0:
                draw.line(((i, 0), (i, 21)), fill=(254, 254, 254), width=4)
        img.save(result_image)


    patdir = os.getcwd()
    print ('Working direktory', patdir)
    with open('0-01 LIST-OF-{}.log'.format(videofile_ext)) as file:
        num_vid_files = [row.strip() for row in file]
    conc = open('0-01 conc.bat', 'w')
    txtmacros = open('0-02MAKROS.txt')
    scr = txtmacros.read()
    for n in range (0, len(num_vid_files)):
       
        png = num_vid_files[n].replace(videofile_ext, '.png')
        #scrpt = """ffmpeg -i {} -i {} -i 0-MARK.png -filter_complex "overlay=x='if(gte(t,0), 320-(t*25), 3)':y=300[a]; [a]drawtext=fontfile=0-FONT.ttf:timecode='00\:00\:00\:00':rate=25:text='{} TC\:':fontsize=27:fontcolor=white:x=220:y=330: box=1: boxcolor=0x000000AA[b]; [b][2:v]overlay " -c:v mpeg4 -b:v 7000k -b:a 256k -acodec mp3 -y +{}""".format(num_vid_files[n], png, num_vid_files[n],num_vid_files[n])
        scrpt = scr.format(num_vid_files[n], png, num_vid_files[n], num_vid_files[n])
        conc.write(scrpt)
        conc.write('\n')

videofile_ext = '.mp4'

make_list()
analiz_video()
make_image()
subprocess.check_call('0-01 conc.bat', shell=True)
print ('E-N-D')




