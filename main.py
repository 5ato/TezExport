test = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]

per_row = 3
one_time = 15


result = []
count_per_row = 0
count_one_time = 0


for i in test:
    if count_one_time % one_time == 0:
        if count_per_row % per_row == 0:
            result.append([[i]])
        else:
            result[-1].append(i)
        count_per_row+=1
    else:
        if count_per_row % per_row == 0:
            result[-1].append([i])
        else:
            result[-1][-1].append(i)
        count_per_row+=1
    count_one_time+=1
        
print(result)
