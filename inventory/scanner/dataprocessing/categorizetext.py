

"""
The purpose of this is to categorize texts where categories are the longest matching strings. 

{
    "category": [string indices].
}

1) Given an array of strings
2) Take the first string
3) Compare string with each string in string_array[1:]
4) The longest possible match is taken as the category.
5) If there is no match, store the string as its own category.
6) Take the second string, and compare with each string in string_array[0, 3:]
7) If the longest possible match is inside categories, then add the index of this string to that match.
8) If the longest possible match is not inside the category, then add the longest possible as its own category.
9) Otherwise take string 2 and store it as its own category.
10) Repeat step 6-9 for the rest of the strings.

"""