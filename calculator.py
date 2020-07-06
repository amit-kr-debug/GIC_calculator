def calculate_gic(start_date1: list, end_date1: list):
    value = 0
    start_date2 = [start_date1[0], start_date1[1], start_date1[2]]
    # print()
    # print("Deposits till 1998")
    value1, str1 = till_mar1998(start_date1, end_date1)
    # print()
    # print("Deposits after 1998")
    value2, str2 = till_end(start_date2, end_date1)
    value = value1 + value2
    # print()
    # print("Total sum = ", value1, " + ", value2, " = ", value)
    return value, str1, str2


def till_mar1998(start_date, end_date):
    OB = 0
    tillmar1998 = ""
    if start_date[2] > 1998:
        return OB
    while start_date[2] <= end_date[2]:
        prevmonth = start_date[1]
        prevyear = start_date[2]
        if start_date[2] < 1982:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                start_date[2] += 1
                start_date[1] = 4
            interest = int(round((OB * months + months / 2 * (2 * 10 + (months - 1) * 10)) * 6 / 1200))
            Total = interest + 10 * months
            OB += Total
        elif start_date[2] == 1982:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                interest = int(round((OB * months + months / 2 * (2 * 10 + (months - 1) * 10)) * 6 / 1200))
                Total = interest + 10 * months
                OB += Total
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                interest = int(round((OB * months + months / 2 * (2 * 20 + (months - 1) * 20)) * 6 / 1200))
                Total = interest + 20 * months
                OB += Total
                start_date[2] += 1
                start_date[1] = 4
        elif start_date[2] < 1985:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                start_date[2] += 1
                start_date[1] = 4
            interest = int(round((OB * months + months / 2 * (2 * 20 + (months - 1) * 20)) * 6 / 1200))
            Total = interest + 20 * months
            OB += Total
        elif start_date[2] == 1985:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                interest = int(round((OB * months + months / 2 * (2 * 20 + (months - 1) * 20)) * 6 / 1200))
                Total = interest + 20 * months
                OB += Total
                start_date[1] = 4
            elif 3 < start_date[1] <= 6:
                months = 7 - start_date[1]
                interest = int(round((OB * months + months / 2 * (2 * 20 + (months - 1) * 20)) * 6 / 1200))
                Total = interest + 20 * months
                OB += Total
                start_date[1] = 7
            else:
                months = 16 - start_date[1]
                start_date[1] = 4
                start_date[2] += 1
                interest = int(round((OB * months + months / 2 * (2 * 80 + (months - 1) * 80)) * 12.5 / 1200))
                Total = interest + 80 * months
                OB += Total
        elif start_date[2] < 1998:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                start_date[2] += 1
                start_date[1] = 4
            interest = int(round((OB * months + months / 2 * (2 * 80 + (months - 1) * 80)) * 12.5 / 1200))
            Total = interest + 80 * months
            OB += Total
        elif start_date[2] == 1998:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                interest = int(round((OB * months + months / 2 * (2 * 80 + (months - 1) * 80)) * 12.5 / 1200))
                Total = interest + 80 * months
                OB += Total
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                interest = int(round(OB * months * 12.5 / 1200))
                Total = interest
                OB += interest
                start_date[2] += 1
                start_date[1] = 4
        elif start_date[2] < 2010:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                interest = int(round(OB * months * 12.5 / 1200))
                OB += interest
                Total = interest
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                interest = int(round(OB * months * 12.5 / 1200))
                OB += interest
                Total = interest
                start_date[2] += 1
        elif start_date[2] == end_date[2] and end_date[2] > 2010:
            months = 9 + end_date[1]
            interest = int(round(OB * months * 8 / 1200))
            OB += interest
            Total = interest
            start_date[2] += 1
        else:
            if start_date[1] <= 3:
                months = 3 - start_date[1] + 1
                interest = int(round(OB * months * 8 / 1200))
                OB += interest
                Total = interest
                start_date[1] = 4
            else:
                months = 16 - start_date[1]
                interest = int(round(OB * months * 8 / 1200))
                OB += interest
                Total = interest
                start_date[2] += 1
        # print(start_date[1], "-", start_date[2], ": ", OB, interest, Total)
        # tillmar1998 += str(start_date[1]) + "-" + str(start_date[2]) + ": "+str(OB)+"    "+str(interest)+"    "+str(Total)+"\n"
        tillmar1998 += str(prevmonth) + "-" + str(prevyear) + ": " + str(OB) + "    " + str(
            interest) + "    " + str(Total) + "\n"
    return OB, tillmar1998


def till_end(start_date, end_date):
    OB = 0
    aftermar1998 = ""
    if start_date[2] < 1998:
        start_date[2] = 1998
        start_date[1] = 4
    elif start_date[2] == 1998:
        if start_date[1] <= 3:
            start_date[1] = 4
    while start_date[2] <= end_date[2]:
        prevmonth = start_date[1]
        prevyear = start_date[2]
        if start_date[2] <= 2000:
            months = 13 - start_date[1]
            interest = int(round((OB * months + months / 2 * (2 * 21 + (months - 1) * 21)) * 12 / 1200))
            start_date[1] = 1
            Total = 21 * months + interest
            OB += Total
            start_date[2] += 1
        elif start_date[2] == 2001:
            months = 13 - start_date[1]
            interest = int(round((OB * months + months / 2 * (2 * 21 + (months - 1) * 21)) * 11 / 1200))
            start_date[1] = 1
            Total = 21 * months + interest
            OB += Total
            start_date[2] += 1
        elif start_date[2] == 2002:
            months = 13 - start_date[1]
            interest = int(round((OB * months + months / 2 * (2 * 21 + (months - 1) * 21)) * 9.5 / 1200))
            start_date[1] = 1
            Total = 21 * months + interest
            OB += Total
            start_date[2] += 1
        elif start_date[2] == 2003:
            months = 13 - start_date[1]
            interest = int(round((OB * months + months / 2 * (2 * 21 + (months - 1) * 21)) * 9 / 1200))
            start_date[1] = 1
            Total = 21 * months + interest
            OB += Total
            start_date[2] += 1

        elif start_date[2] == end_date[2]:
            months = end_date[1] - start_date[1] +1
            interest = int(round((OB * months + months / 2 * (2 * 21 + (months - 1) * 21)) * 8 / 1200))
            start_date[1] = 1
            Total = 21 * months + interest
            OB += Total
            start_date[2] += 1

        else:
            months = 13 - start_date[1] + 1
            interest = int(round((OB * months + months / 2 * (2 * 21 + (months - 1) * 21)) * 8 / 1200))
            start_date[1] = 1
            Total = 21 * months + interest
            OB += Total
            start_date[2] += 1
        # print(start_date[1], "-", start_date[2], ": ", OB, interest, Total)
        # aftermar1998 += str(start_date[1]) + "-" + str(start_date[2]) + ": "+str(OB)+"   "+str(interest)+"   "+str(Total)+"\n"
        aftermar1998 += str(prevmonth) + "-" + str(prevyear) + ": " + str(OB) + "    " + str(
            interest) + "    " + str(Total) + "\n"
    return OB, aftermar1998


def calculator(start_date_str: str, end_date_str: str):
    starting_date = [int(start_date_str[0:2]), int(start_date_str[3:5]), int(start_date_str[6:])]
    ending_date = [int(end_date_str[0:2]), int(end_date_str[3:5]), int(end_date_str[6:])]
    TotalSum, str1, str2 = calculate_gic(starting_date, ending_date)
    # print(str1, str2)
    return TotalSum, str1, str2
