print "Input the directory you has tag_tag.json format data , to load preloaded questions type  :::   question_json_processing/questions_json"
execfile("./question_json_processing/load_questions_from_json.py")

print "\n\nInput the directory which contains direct question data including tags , to load preloaded questions type  :::   question_json_processing/song_data.json"
execfile("./question_json_processing/song_data_processing.py")
