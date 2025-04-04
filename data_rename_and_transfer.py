import datetime
import glob
import os


def get_path(source):
    paths={
        'Behaviour' : os.path.join('D:\\', 'behavior\\'),
        'Widefield' : os.path.join('C:\\', 'Experiment', 'WideFieldImaging', 'data\\'),
        'Twophoton' : '',
        'Video'     : os.path.join('F:\\', 'Video_data\\'),

        'Behaviour_svr' : os.path.join('Training\\'),
        'Recording_svr' : os.path.join('Recording', 'Behaviour\\'),
        'Widefield_svr' : os.path.join('Recording', 'Imaging\\'),
        'Twophoton_svr' : os.path.join('Recording', 'Imaging\\'),
        'Video_svr'     : os.path.join('Recording', 'Video\\')

    }
    return paths[source]

def create_server_struct(mouse_name):
    """
    Generate folders and subfolders for server for a new subject.
    """
    root = 'M:\\data\\'
    main_dir =['Anatomy', 'IOS', 'Recording', 'SLIMS', 'Training']
    subdirs = ['Behaviour', 'Imaging', 'Video']

    for dir in main_dir:
        try: os.makedirs(os.path.join(root+mouse_name, dir))
        except OSError: pass

        if dir == 'Recording':
            for dir2 in subdirs:
                try: os.makedirs(os.path.join(root+mouse_name, dir, dir2))
                except OSError: pass

def get_data_type():
    """
    Assign type of data acquired by computer. Computer name can be found in Windows -> About -> Device name. 
    """

    pcname = os.environ['COMPUTERNAME']

    if pcname in ['SV-07-051', 'SV-07-072', 'SV-07-073', 'SV-07-068']:
        source = 'Behaviour'

    elif pcname in ['SV-07-091', 'SV-07-074']:
        source = 'Widefield'

    elif pcname in ['SV-07-093', 'SV-07-094']:
        source = 'Video'

    elif pcname in ['imaging_comp']:
        source = 'Twophoton'

    elif pcname in ['ephys_comp']:
        source = 'Ephys'

    return source


def get_associated_computers():
    """
    Assign type of data acquired by computer. Computer name can be found in Windows -> About -> Device name. 
    """

    pcname = os.environ['COMPUTERNAME']

    if pcname in ['SV-07-051']:
        source = {
            "behaviour": os.path.join(r"E:\\", "behavior"),
            "widefield": os.path.join(r"\\sv-07-091", "Experiment", "WideFieldImaging", "data"), 
            "bhv_cam_top": os.path.join(r"\\sv-07-093", "bhv_cam_top"), 
            "bhv_cam_side": os.path.join(r"\\sv-07-093", "bhv_cam_side")}

    elif pcname in ['SV-07-068']:
        source = {
            "behaviour": os.path.join(r"D:\\", "behavior"),
            "widefield": os.path.join(r"\\sv-07-074", "Experiment", "WideFieldImaging", "data"), 
            "bhv_cam_top": os.path.join(r"\\sv-07-094", "bhv_cam_top"), 
            "bhv_cam_side": os.path.join(r"\\sv-07-094", "bhv_cam_side")}


    return source

def transfer_data():
    """
    Enter a date and save data from computer into corresponding folder in server.
    """

    usr_date = int(input('Enter date (yyyymmdd) or # days from today: '))

    if len(str(usr_date)) < 6:
        date = int((datetime.date.today() - datetime.timedelta(days = usr_date)).strftime('%Y%m%d'))
    elif len(str(usr_date)) == 8:
        date = int(usr_date)
    else:
        date = int(input('Input date was incorrect, try again in yyyymmdd format: '))

    print('Transferring data from session {}'.format(date))

    data_path = get_associated_computers() # Find folders where to find data
    
    folders = glob.glob(data_path["behaviour"] + '\\*\\**') # List of folders in data_path

    for path in folders:
        if str(date) not in path:
            continue

        session = path.split('\\')[-1]
        animalID = session.split("_")[0]
        create_server_struct(animalID) # If first time for a new animalID, generate folder structure according to lab standards

        server_path = os.path.join('\\\\sv-nas1.rcp.epfl.ch\Petersen-Lab', 'data', animalID, 'Training', session)

        if not os.path.isdir(server_path):
            os.makedirs(server_path)

        os.system("""xcopy "%s" "%s" /i /s /y /d""" % (path + '\\', server_path + '\\')) # Copy data, if not copied already

        wf_path = os.path.join(data_path["widefield"], animalID, str(date))

        if os.path.exists(wf_path) and len(os.listdir(wf_path))==1:
            print(" ")
            print(f"Found widefield data for animal {animalID} date {date}")
            os.rename(os.path.join(wf_path, os.listdir(wf_path)[0]), 
                    os.path.join(wf_path, f"{session}.mj2"))

            server_path = os.path.join('\\\\sv-nas1.rcp.epfl.ch\Petersen-Lab', 'data', animalID, 'Recording', 'Imaging', session)

            if not os.path.isdir(server_path):
                os.makedirs(server_path)

            os.system("""xcopy "%s" "%s" /i /s /y /d""" % (os.path.realpath(wf_path)+"\\", os.path.realpath(server_path)+"\\")) # Copy data, if not copied already

        elif os.path.exists(wf_path) and len(os.listdir(wf_path))>1:
            print(" ")
            print(f"Found multiple widefield data for animal {animalID} date {date}")
            root = path[:-6]
            curr_files = [file for file in folders if root in file]
            file_idx = curr_files.index(os.path.join(os.path.commonpath(curr_files), session))
            
            os.rename(os.path.join(wf_path, os.listdir(wf_path)[file_idx]), 
                    os.path.join(wf_path, f"{session}.mj2"))
            
            server_path = os.path.join('\\\\sv-nas1.rcp.epfl.ch\Petersen-Lab', 'data', animalID, 'Recording', 'Imaging', session)

            if not os.path.isdir(server_path):
                os.makedirs(server_path)     

            os.system("""xcopy "%s" "%s" /i /s /y /d""" % (os.path.realpath(os.path.join(wf_path, f"{session}.mj2")), 
                                                        os.path.realpath(server_path))) # Copy data, if not copied already
            
        bhv_top_path = os.path.join(data_path["bhv_cam_top"], animalID, str(date))
        bhv_side_path = os.path.join(data_path["bhv_cam_side"], animalID, str(date))

        if os.path.exists(bhv_top_path) and len(os.listdir(bhv_top_path))==1:
            print(" ")
            print(f"Found behaviour recordings for animal {animalID} date {date}")
            os.rename(os.path.join(bhv_top_path, os.listdir(bhv_top_path)[0]), 
                    os.path.join(bhv_top_path, f"{session}_topview.avi"))

            os.rename(os.path.join(bhv_side_path, os.listdir(bhv_side_path)[0]), 
                    os.path.join(bhv_side_path, f"{session}_sideview.avi"))

            server_path = os.path.join('\\\\sv-nas1.rcp.epfl.ch\Petersen-Lab', 'data', animalID, 'Recording', 'Video', session)

            if not os.path.isdir(server_path):
                os.makedirs(server_path)

            os.system("""xcopy "%s" "%s" /i /s /y /d""" % (os.path.realpath(bhv_top_path)+"\\", os.path.realpath(server_path)+"\\")) # Copy data, if not copied already
            os.system("""xcopy "%s" "%s" /i /s /y /d""" % (os.path.realpath(bhv_side_path)+"\\", os.path.realpath(server_path)+"\\")) # Copy data, if not copied already

        elif os.path.exists(bhv_top_path) and len(os.listdir(wf_path))>1:
            print(" ")
            print(f"Found multiple behaviour recordings for animal {animalID} date {date}")
            root = path[:-6]
            curr_files = [file for file in folders if root in file]
            file_idx = curr_files.index(os.path.join(os.path.commonpath(curr_files), session))
            
            os.rename(os.path.join(bhv_top_path, os.listdir(bhv_top_path)[file_idx]), 
                    os.path.join(bhv_top_path, f"{session}_topview.avi"))

            os.rename(os.path.join(bhv_side_path, os.listdir(bhv_side_path)[file_idx]), 
                    os.path.join(bhv_side_path, f"{session}_sideview.avi"))
            
            server_path = os.path.join('\\\\sv-nas1.rcp.epfl.ch\Petersen-Lab', 'data', animalID, 'Recording', 'Video', session)

            if not os.path.isdir(server_path):
                os.makedirs(server_path)     

            os.system("""xcopy "%s" "%s" /i /s /y /d""" % (os.path.realpath(os.path.join(bhv_top_path, f"{session}_topview.mj2")), 
                                                        os.path.realpath(server_path))) # Copy data, if not copied already
            os.system("""xcopy "%s" "%s" /i /s /y /d""" % (os.path.realpath(os.path.join(bhv_side_path, f"{session}_sideview.mj2")), 
                                                        os.path.realpath(server_path))) # Copy data, if not copied already
            

if __name__ == '__main__':
    transfer_data()