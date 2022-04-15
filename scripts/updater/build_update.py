 #!/usr/bin/env python3
 
 def make_update_algorythm():
     """Creates file with an update algorythm
        
     """
     print('build an update algorythm\nchoose \
         options and print requires info\n')
     kind = 0
     
     while kind != 2:
         kind = int(input()) # 1 - file, 2 - command
         
         if kind == 1:
             print('enter filename: ')
             file_name = input()
             
