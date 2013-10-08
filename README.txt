1. Jason Ibrahim

2. 	There were many difficulties I faced in implementing this router.
	Routing loops and strange behaviors upon links being taken down
	and coming back up were the most common. These bugs took a very
	long time to resolve and I went through several iterations of
	the RIPRouter class and many git commits before finally coming
	upon a solution that correctly implemented poison reverse and
	implicit withdrawals. These features took a long time for me
	to understand and so I went through countless hours of staring
	at the simulation trying to understand how everything was communicating.
	At one point, I had correctly implemented the poison reverse and
	the implicit withdrawals, but the routers still contained old values
	that were no longer any good. It  wasnt until I decided that I should
	refresh my best costs upon links going down and discovering new destinations
	that I finally got it to work. Once I got it to work I spent a few hours
	going through every edge case I could think of, but the RIPRouter is
	finally invincible. Clocked in about 60-70 hours on this project.

3.	A feature not mentioned that would improve the functionality of this
	Router would be to have a centralized master router that calculates
	all of the optimal routes and pushes these tables to each router.
	That way routers don't have to waste time sending updates to each other
	until they all converge. Each router would send their direct links to
	the master router, the master router would create an optimal table
	for each router, and push these tables to each router. In this scheme,
	only two messages are sent to form tables - one to the master, and one
	from the master to the router.

4.	For extra credit, I analyzed the number of updates sent and I tried to
	optimize how my routers were sending updates. I believe I came across
	a solution that converges quickly and sends relatively few routing updates. This information is contained in the file AnalyzingUpdates.pdf. In that file is the array of the number of updates sent, as well as the plot of the updates vs the number of routers in the network. I found that the growth is quadratic as a function of the number of the routers in the network. While this may not be the kind of linear growth that is found in the ideal model of router networks, the solution I have implemented finds cheap routes reliably and with relatively little computational complexity. I believe my solution sends a small number of routing updates upon discovery, and even less once the table has converged for the first time.

	I have included the scenario and the shell script I used to run my tests. The scenario can be found in scenarios/octagon.py and the shell script can be found
	in the main project1 directory and is called analyze.sh. I have included all of these files.
