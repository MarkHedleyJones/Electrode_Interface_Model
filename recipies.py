import lib.solutions.pbs.recipie

def make(solutions):
    #=============================================================================
    # Make a solution of Phosphate Buffered Saline
    #=============================================================================
    rep = lib.solutions.pbs.recipie.PBS_Recipie(solutions)
    rep.print_instructions()


#==============================================================================
# For six roughly doubling solutions
#==============================================================================
print('For six roughly doubling solutions...')
print
concentrations = [0.025,
                  0.05,
                  0.1,
                  0.25,
                  0.5,
                  1.0]
volumes = [700 for x in concentrations]
solutions = zip(volumes, concentrations)
make(solutions)

print('----------------------------------------------------------------------')
#==============================================================================
# For one 5L stock solution
#==============================================================================
print('For one 5L stock solution...')
print
solution = [(5000, 1.0)]
make(solution)
