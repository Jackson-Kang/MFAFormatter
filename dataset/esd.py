from utils import do_multiprocessing, get_filelist, copy_file, read_meta, write_meta, create_dir

import os, itertools, sys

class EmotionalSpeechDataset():

	def __init__(self, dataset_path, preprocessed_file_dir, language='english'):

		self.dataset_path = dataset_path
		dataset_name = dataset_path.split("/")[-1]
		self.preprocessed_file_dir = preprocessed_file_dir

		create_dir(preprocessed_file_dir)
		self.preprocessed_file_dir = create_dir(os.path.join(preprocessed_file_dir, dataset_name))

		self.emotions = ["Angry", "Happy", "Neutral", "Sad", "Surprise"]

		if language=="english":
			self.speaker_ids = ["00{}".format(speaker_id) for speaker_id in range(11, 21)]	# Only use english dataset
		elif language == "chinese":
			self.speaker_ids = ["00{}".format(speaker_id) for speaker_id in range(0, 11)]  # Only use chinese dataset
		else:
			self.speaker_ids = ["00{}".format(speaker_id) for speaker_id in range(0, 21)]


	def job(self, info):
		wav_filepath, transcript, save_dir = info
		if transcript in ["", "\t\n", "\t", "\n"]:			
			return

		if len(transcript.split("\t")) !=3:
			temp, emotion = transcript.split("\t")
			transcript_filename, transcript = temp[:11], temp[12:]
		else:
			transcript_filename, transcript, emotion = transcript.split("\t")

		filename =  wav_filepath.split("/")[-1]
		if transcript_filename not in filename:
			print("[ERROR] transcript filename and wav-filename doesn't match!")
			print("\t\t transcript_filename: {} vs. wav-filename: {}".format(transcript_filename, filename))		
			sys.exit(0)
			return

		wav_savepath = os.path.join(save_dir, filename)
		transcript_savepath = os.path.join(save_dir, filename.replace(".wav", ".lab"))

		copy_file(wav_filepath, wav_savepath)		
		write_meta(transcript, transcript_savepath)


	def run(self):

		wav_filepaths = get_filelist(os.path.join(self.dataset_path, "**", "**", "**"), file_format="wav")
		wav_filepaths = [(wav_filepath.split("/")[-1], wav_filepath) for wav_filepath in wav_filepaths]
		wav_filepaths.sort(key=lambda x: x[0])
		_, wav_filepaths = list(zip(*wav_filepaths))

		wav_filelist = [ filepath for filepath in wav_filepaths if filepath.split("/")[-1].split("_")[0] in self.speaker_ids]
		
		transcripts = [read_meta(os.path.join(self.dataset_path, speaker_id, "{}.txt".format(speaker_id))) 
									for speaker_id in self.speaker_ids]
		transcripts = list(itertools.chain(*transcripts))


		save_dirs = [create_dir(os.path.join(self.preprocessed_file_dir, "{}_{}".format(wav_filepath.split("/")[-4], 
								wav_filepath.split("/")[-3]))) for wav_filepath in wav_filelist]		

		if len(wav_filelist) != len(transcripts):
			print("[ERROR] num of wavs and num of transcripts doesn't match! ({} vs. {})".format(len(wav_filelist), len(transcripts)))
			return

		file_infos = list(zip(wav_filelist, transcripts, save_dirs))

		do_multiprocessing(job=self.job, tasklist=file_infos)

