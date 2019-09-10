#-*- coding: UTF-8 -*-  
import os
from PIL import Image
import imageio
 
def analyseImage(path):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode 
    before processing all frames.
    '''
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results
 
 
def processImage(path):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyseImage(path)['mode']
    
    im = Image.open(path)
 
    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')

    # 生成的列表
    image_list = [];
    
    try:
        while True:
            print ("saving %s (%s) frame %d, %s %s" % (path, mode, i, im.size, im.tile))
            
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)
            
            new_frame = Image.new('RGBA', im.size)
            
            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)
            
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            new_frame.save('%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')
            image_list.append(('%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i)));
 
            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass

    return image_list;

def get_new_list(before_list, num):
    before_list_length = len(before_list);

    # 如果总帧数列表不超过限制的帧数,则直接返回
    if(before_list_length<=num):
      return before_list;
    # 如果总帧数列表超过了限制的帧数, 则返回"瘦身"后的列表
    else:
      # 返回新的列表
      after_list = [];
      # 取gif帧的间隔
      gap = len(before_list) // num + 1;
      for (f_index, f_value) in enumerate(before_list):
        if(f_index % gap == 0):
          after_list.append(f_value)
      return after_list


def create_gif(image_list, gif_name):
    frames = []
    for image_name in image_list:
        frames.append(imageio.imread(image_name))
    # Save them as frames into a gif 
    imageio.mimsave(gif_name, frames, 'GIF', duration = 0.1)
    return
 

# 读取同级目录下所有gif
# 获取当前目录下所有md文件
def get_gif_files(md_dir):
    gif_files = [];
    for root, dirs, files in sorted(os.walk(md_dir)):
        for file in files:
            # 获取.gif或.GIF结尾的文件
            if(file.endswith(".gif")or(file.endswith(".GIF"))):
                file_path = os.path.join(root, file)
                print(file_path)
                gif_files.append(file_path)
    return gif_files


def main():
    gif_list = get_gif_files("./");
    for (gif_index, gif_value) in enumerate(gif_list):
      image_list = processImage(gif_value);
      print("===>>>", gif_value);
      new_gif_name = 'new_'+ gif_value.split("/")[-1]
      new_image_list = [];
      # 对数组进行瘦身
      new_image_list = get_new_list(image_list, 30)
      create_gif(new_image_list, new_gif_name);
      # 删除生成的临时静态图片
      for image_path in image_list: 
          os.remove(image_path);


 
if __name__ == "__main__":
    main()