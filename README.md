# pololu-tic-driver
Pololu's Tic driver for Linux.

## WHAT IS THIS
First of all, you may be thinking that there are a only one source file. Yes, one file to rull them all!

## HOW TO
The good thing about developing test in .py is that you don't have to compile anything, just plug and play

> But careful!

You should have the TIC's software installed. 

> Check https://www.pololu.com/docs/0J71/3.2

It's a very easy step, I promise ;)

## PY FILE

You will need a FTDI converter since the Pololu doesn't have any USB virtual port.

> That's why it doesn't appear in any /dev/tty* port

And, that's why I use the TIC's software as basis of this driver.

### pololu_cmd.py

> Hallelujah!

Yes, there's a file that works without FTDI or magic. It just needs the TIC software mentioned above. Please, install it, a bunch of unicorns will be happier!

Still confused? Type:

    ./pololu_cmd.py

and enjoy the magic!

You can also import this file in order to use its functions.

If you run this file directly, the TIC will perform 5 test: 1 turn, 2 turns, 3 turns...

Every test will be recorded in a csv file, saved in a directory for the 12 test, named as __test_yyyymmdd_HHMMSS__. Easy, right? Just dive inside and you will find each test file named in the same way.

> You can also edit this file to include other functionalities. M-A-G-I-C!
