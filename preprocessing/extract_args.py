import re 
import json
import pandas as pd 

def extract(data):
  new_args = data['args']
  new_args_df = pd.DataFrame(new_args)
  def strip_string(input_str):
      """
      Takes an input string and replaces specific
      puncutation marks with nothing

      Args:
          input_str: The string to be processed

      Returns:
          The processed string
      """
      assert isinstance(input_str, str)
      return input_str.replace("'", '"')

  new_args_df['stripped_args'] = new_args_df['args'].apply(strip_string)

  def remove_value_field(data: str) -> str:
      # Regex pattern to match the "value" field and remove everything between '{' and '}'
      pattern = r'"value":\s*"\{.*?\}",?'

      # Replace the matched "value" field and its content with an empty string
      result = re.sub(pattern, '', data)

      # Clean up any extra commas left behind
      result = re.sub(r',\s*}', '}', result)  # Trailing commas before closing braces
      result = re.sub(r',\s*]', ']', result)  # Trailing commas before closing brackets
      result = re.sub(r'\{\s*,', '{', result)  # Leading commas after opening braces
      result = re.sub(r'\[\s*,', '[', result)  # Leading commas after opening brackets


      return result.strip()

  def rem_value(data:str) -> str:
      pattern_2 = r',?\s*"value":\s*[^}]+(?=})'
      result = re.sub(pattern_2, '', data)
      return result.strip()

  new_args_df['stripped_args_drop_value'] = new_args_df['stripped_args'].apply(remove_value_field)
  new_args_df['stripped_args_drop_value'] = new_args_df['stripped_args_drop_value'].apply(rem_value)


  result = {'name': [], 'type': []}
  def extract_values(row,result):
      try:
          items= json.loads(row)
      except json.JSONDecodeError:
          print(f"Error decoding JSON: {row}")
          return
      # Parse the row into a list of dictionaries
      # Create a dictionary with lists for each key

      for item in items:
          if item.get('name') not in result['name']:
            result['name'].append(item.get('name'))
          if item.get('type') not in result['type']:
            result['type'].append(item.get('type'))


  arg_features = ["name_sockfd","type_int","type_struct sockaddr*","type_const char*","type_dev_t","type_unsigned long","type_int*","type_mode_t","type_unsigned int","type_struct linux_dirent64*","type_struct stat*","type_size_t","type_const char*const*","type_void*","type_pid_t","type_u32","type_const void*","type_uid_t","type_sigset_t*","type_gid_t","type_gid_t*","type_union bpf_attr*","name_addr","name_addrlen","name_pathname","name_flags","name_dev","name_inode","name_dirfd","name_mode","name_cap","name_fd","name_dirp","name_count","name_statbuf","name_argv","name_stack","name_parent_tid","name_child_tid","name_tls","name_domain","name_type","name_protocol","name_option","name_arg2","name_arg3","name_arg4","name_arg5","name_oldfd","name_newfd","name_pid","name_sig","name_uid","name_gid","name_ruid","name_euid","name_target","name_owner","name_group","name_backlog","name_fsuid","name_rgid","name_egid","name_fsgid","name_name","name_source","name_filesystemtype","name_mountflags","name_data","name_cmd","name_attr","name_size","name_linkpath"]


  for index, row in enumerate(new_args_df['stripped_args_drop_value']):
      #print(f"Row {index + 1}")
      extract_values(row,result)  # Extracted dictionary for the row

  def modify_columns_to_df(df, names, types):
      # Iterate over names and types to create new columns in the desired format
      for feature in arg_features:
              df[f'{feature}'] = 0
      return df


  new_args_df = modify_columns_to_df(new_args_df, result['name'], result['type'])

  def update_columns_from_json(df):
      # Iterate over each row
      for idx, row in df.iterrows():
          # Parse the JSON in the 'stripped_args_drop_value' column
          try:
              row_extracted = {'name': [], 'type': []}
              extract_values(row['stripped_args_drop_value'],row_extracted)


              # Update the corresponding 'name_{name}' and 'type_{type}' columns to 1
              for name in row_extracted['name']:
                  if f'name_{name}' in df.columns:
                      df.at[idx, f'name_{name}'] = 1
              for typ in row_extracted['type']:
                  if f'type_{typ}' in df.columns:
                      df.at[idx, f'type_{typ}'] = 1

          except json.JSONDecodeError:
              print(f"Error decoding JSON at row {idx}")

      return df

  # Update the DataFrame
  new_args_df = update_columns_from_json(new_args_df)
  #Exclude the columns 'args', 'stripped_args', and 'stripped_args_drop_value'
  exclude_columns = ['args', 'stripped_args', 'stripped_args_drop_value']

  # Create a boolean DataFrame, where all columns except the excluded ones are checked for 0
  mask = new_args_df.drop(columns=exclude_columns).eq(0)

  # Get the indexes of rows where all selected columns are 0
  rows_with_all_zeros = mask.all(axis=1)

  # Store the indexes of the rows that meet the condition
  indexes = rows_with_all_zeros[rows_with_all_zeros].index.tolist()
  new_args_df_filtered = new_args_df.drop(columns=exclude_columns)
  
  
  # Concatenate the filtered `sample_df` to the `data` DataFrame
  final_data= pd.concat([data,new_args_df_filtered], axis=1)
  # Drop the rows with the indexes specified in the `indexes` list
  final_data_dropped = final_data.drop(indexes)

  # Optionally, reset the index if you want a continuous index after dropping rows
  final_data = final_data_dropped.reset_index(drop=True)
  final_data = final_data.drop(columns=[col for col in ['sus','userId','evil','processId','timestamp','parentProcessId','args'] if col in final_data.columns])

  return final_data  