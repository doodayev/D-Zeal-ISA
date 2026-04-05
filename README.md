# D-Zeal-ISA
This is a 64-bit CPU Instruction Set Architecture by the name of "D-Zeal". 64-bit registers, 64-bit memory addresses, 64-bit instructions. 
Also, every instruction has its instruction fields in multiples of 8 so you can read each instruction in hexadecimal format quite easily. 
Shoutout to "BRH - French SoC Enjoyer" (he goes by "0BAB1" on Github) and David Harris and Sarah Harris.

## What's the point? Why did I make this
I made this for my thesis. I'll link that soon I hope. 
The point of the thesis is that every few years some people and organizations decide that we need yet another layer of abstraction to make
our lives 'easier' but in reality it makes our lives worse, more painful, and more expensive.
There is some sort of war against writing native code, against letting people understand what they're doing.
Things move too fast for the old geezers to get used to things and actually learn and even the young can't really keep up even though
they may think they're keeping up.

Like for example with videogames the young think that so long as they buy a physical game they keep the game, but that's not really true anymore.
A lot of physical releases these days contain only a part of the game or might not even include a disc at all or if it does it contains very little
of the actual game. Not only that, many games these days rely on a central server that if these servers were to disappear, then that Blu-Ray disc
becomes a coaster for their coffee and nothing more. 

Can you play Ubisoft's "The Crew" anymore? Can you play the original "Overwatch"? No, even though they had physical releases.
Yet as I said many young adults don't understand this, much like they may not understand a lot of other things.

So I'm saying to the world. Stop! Go back! Back the other way but not necessarily back in time.
We say to people "too much of a good thing can be bad for you" right? Well too much abstraction has become a poison for us.

People think that writing assembly code is some sort of magic and I was even taught in community college that "nobody ever reads machine code".
Well who the heck is going to write your compiler then? Do you think LLVM was made by fairies and elves? Someone has to do that.
Someone also has to make the chips. So clearly somebody has to actually learn these things.

If we are fine with adding so many abstractions to our software, which in consequence causes so much overhead that we need hardware that
is literally ten times or a hundred times faster than we had in the past to do the same things people were doing on for example 
Windows 95 with an Intel 486 and 16MB of RAM. Now should we go back to using Windows 9x and single core CPUs? No.
I'm not saying that, though I think they still have their place and should still be an option.

But what I am saying is that if we're going to abuse hardware designers and keep whipping them to keep squeezing out performance
just to run horribly optimized code, well how about we cut out the middleman and just add a little of our own abstractions
into the CPU itself?

### What are the abstractions and features in D-Zeal? 
* 64-bit long instructions that has each bitfield be either 8, 16, or 32-bits long.
*  256 general purpose registers, only one of which as of now has a special purpose, 
and that's the "0" register which always holds the value of zero.
* Since immediate fields are always 32-bits long, loading in values, branching, and jumping is so easy.
No more restrictive sizes like 12-bits like in RISC-V. You can load a 64-bit immediate in just two instructions
and jump to a 64-bit address similarly in just two instructions.
* Opcodes being 16-bit means there's no need for a field like funct3 or funct7. 
65,536 opcodes ought to be enough for anyone. If it isn't? I'm judging you.
* Like RISC-V there are 6 main categories:
  * R-type (Register to Register)
  * I-type (Immediate to Register)
  * S-type (Storing stuff to registers)
  * B-type (Branch instructions),
  * U-type (loading "upper immediates")
  * J-type (Unconditional Jumps)
R-type opcodes start with "A" like A000 is for an R-type add. I-type starts with "B" (Add Immediate is B000), and so on.
People who wish to extend the ISA with more categories can use 0 through 9.
* Technically there is a funct4 field being used but it exists as the last digit of the opcode. 
A003 for example, the 3 means it's a subtraction. But that digit only gets used like that for basic ALU operations.
If there was an instruction like A086 to represent something, that 6 wouldn't be used to signal the ALU probably.
* The Machinecode is readable enough that I did not need to write an assembler or translator. I just looked at the
hexadecimal and wrote the testprogram you see in "test_imemory.hex"
* Since every instruction is 64-bits long and every instruction can be identified by its category by looking at the
first digit, and every opcode itself is clear in what it does, if anyone ever takes this ISA seriously, it should 
hopefully make reverse engineering programs written for it much easier if someone releases a binary for it and 
then loses the source code. They can just open up a hex editor and read it directly. Every 16 hex digits is one instruction
and they can just read 16-digits per line (so long as they know where the data ends and the instructions begin).

Long story short, I want people to get used to writing assembly code again, be more comfortable with reading machine
and reverse engineering, as well as become a bit more familiar with chip design. I also came to really appreciate
cocotb as a testbench "language". Despite my problems with Python, it was much easier than writing testbenches in
System Verilog.

## Dependencies
I used verilator for my simulator (specifically this version: "Verilator 5.043 devel rev v5.042-236-gc35dde7c9") 
and I used cocotb v2.0.1. I also of course used "make". 

Let me clear! If you wish to do what I did and follow 0BAB1/French SoC Enjoyer's guide because you're
more interested in RISC-V or wish to make your own ISA and follow in his footsteps, some of his code
is meant for a version prior to cocotb v2 and a few things don't work. I had to fix those for my own ISA.
There's also a couple of typos in his guide early on. So keep it in mind! Otherwise it's a great guide
and honestly I'm only upset at cocotb and the whole Python philosophy of breaking things every few versions.
They just can't leave things alone I guess. 

Why not use an older version of cocotb if it's a problem? Because those versions will break on newer versions
of Python. "New" in this case meaning Python 3.13 which is already a bit old. We already have Python 3.14 
actually but Pyhon 3.13 was what came with Debian 13 which is the base of my current Linux distro (MX Linux).

## The RISC-V CPU that the French guy made
"BRH - French SoC Enjoyer" aka 0BAB1 made a RISC-V CPU based off the one in the book: 
"Digital Design and Computer Architecture RISC-V Edition" by David Harris and Sarah Harris.
I just want to make that VERY clear. I want to give credit where it's due.

This is the repository of the 0BAB/SoC Enjoyer:
https://github.com/0BAB1/HOLY_CORE_COURSE

This is the link to the Harris textbook:
https://www.sciencedirect.com/book/monograph/9780128200643/digital-design-and-computer-architecture

The book is good, but keep an eye out for a new RISC-V textbook David Harris is also working on based on the OpenWally core as that one is gonna feature a 5 stage pipeline design
and will be a lot more "complete" from what I told. It will be a more complete CPU but also do a better job of teaching assembly and what-not.
I was looking forward to it releasing on March 2026 but it got delayed. So I wasn't able to look at it before I had to turn in my thesis in the middle of April.
