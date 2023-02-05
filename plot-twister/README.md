## **Plot Twister**

### **Introduction**
Plot Twister is a simple, versatile engine for any range of text adventure games. The only thing required to use it is Python.
Keep reading to get started!

### **Playing the Game**
*This is where you'll find all of the random rules and other helpful things to play this game.*

This isn't case-sensitive, you can type uppercase or lowercase.

If you see '`...`' at the bottom of the line, and the options
aren't showing up, press enter to continue.

#### **Builtins**
Here are some built-in commands to make playing the game easier:
* type '`-b`' or '`-back`' to go back one choice
* type '`-r`' or '`-restart`' to restart game
* type '`-d`' or '`-debug`' to view details about options
* type '`-q`' or '`-quit`' to quit game

#### **Number Mode**
If the person who created the story made one of the options too long for your liking, type '`-#`' to enter number mode.  
In number mode, you can type the number of the option instead of the text. Type '`-a`' to switch back.

### **Creating a Story**

Let's start with an example:

```
[>] start
[=] You are on top of a building
  [>] jump off
  [-] Ouch!
  [>] go to bed
  [=] You wake up and hear a helicopter.
    [>] hide
    [-] Too late for that.
  [>] climb down
  [-] You fall off halfway down.
```
There's a lot of odd punctuation and stuff in that, but I'll explain it.

These are all of the different elements:
* **Indentation** - How much progress you've made.
* **Symbol** - What the line is (an option, a fail, an ending, etc).
* **Message** - The rest of the line. This is the text that gets displayed.

#### **Indentation**
The indentation level will increase with every choice you encounter while playing the game.  
Example: After 5 choices, there should be 5 tabs at the start of the line.

#### **Symbol**
IMPORTANT: The symbol is always inside square brackets.  
Here are some line types, and what symbols to use for them:
* **Choice** - This will show up in the options list. Marked with a greater than sign (`>`).
* **Secret choice** - This will not show up in the options list, but it can be typed. Marked with a less than sign (`<`)
* **Fail** - The message that displays when the player is forced to try again. Marked with a hyphen (`-`).
* **Secret fail** - This is like a normal fail message, but it displays the word "FAIL" after the rest of the message. Marked with an underscore ( `_` ).
* **Not-a-fail** - This is just like a fail, but the word "FAIL" is not displayed. Marked with a tilde (`~`).
* **End** - The message that displays when the game is ended. Marked with a plus sign (`+`).
* **Branch** - The message that displays when the player is able to choose between a new set of options. Marked with an equals sign (`=`)

If you've run any of my stories, you've probably noticed some multi-line messages.  
To write a multi-line message, you have to start out the section with a symbol from above (a fail, end, or branch symbol).
There are 2 different options for the next lines, so I'll explain those here:
* **Instant print** - These lines will print when the previous parts of the message do. Marked with a space.
* **Delay print** - These lines will print soon after the previous parts of the message, but with a slight delay. Marked with a comma.
* **Manual print** - These lines will print when the user presses enter. Marked with a period.

#### **Extra Space**
It doesn't actually matter what symbol goes here. There does need to be one, though.

#### **Message**
If your line starts with a greater than sign, this is what will show up in the options.  
If not, this will show up after the user types in their choice.

#### **Conclusion**
Now that you know all that, see if you can make sense of that example above.  
Even better, try and make your own story!

### **Developers**
If something is bugging you, or you just want to play around with the engine, many elements of it are easy to change.

#### **Easily Changeable Features**
Story files currently have a set format. However, it can be changed.
After changing the format, all you will need to do is change the variables `S` and `M` to the letter index of the symbol in the line, and the index of the first letter of the message, respectively.
If you want to change the symbols, you will need to update the `symbols` list and change all the occurrences of the old symbol (most of them are in the message section, but use Ctrl+F to find the others).

You will notice a delay after some actions. This can also be modified.
Search for `time.sleep()`, and adjust the delay however you want.
