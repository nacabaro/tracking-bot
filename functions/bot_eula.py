def agree_eula():
    # Reads the file of the mandatory eula agreement, followed by the first three lines. After that, read if the eula
    # was accepted. If it was not, print to terminal that it failed and stop the bot from running.
    f = open("configs/eula.txt", "r")
    f.readline()
    f.readline()
    f.readline()
    eula = f.readline().strip("\n")
    f.close()

    if eula == "eula=true":
        return True
    else:
        print("You must agree to the eula before using the bot. To do so edit the file inside configs/eula.txt")
        print("You can read the eula here: https://github.com/nacabaro/tracking-bot/blob/main/README.md#disclaimer")
        return False
