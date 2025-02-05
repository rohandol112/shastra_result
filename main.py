from shastra_result.scrapper import open_chrome, change_view_per_page, extract_data, move_to_next_page, save_data, close_driver
from cleaner import clean_csv
from combiner import combine_files

# Scrapper
open_chrome()
change_view_per_page()

extract_data()      # extract 1st page data
move_to_next_page(0)     # move to 2nd page

extract_data()      # extract 2nd page data 
move_to_next_page(1)  # move to 3rd page

extract_data()  # extract 3rd page data

# save data
save_data()

# Cleaner
clean_csv()

# Combiner
combine_files()

# close driver
close_driver()
