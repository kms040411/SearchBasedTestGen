import astor

for i in range(1, 6):
    f = open("result" + str(i) + ".txt", "w")
    ast = astor.parse_file("sample" + str(i) + ".py")
    f.write(astor.dump_tree(ast))
    f.close()