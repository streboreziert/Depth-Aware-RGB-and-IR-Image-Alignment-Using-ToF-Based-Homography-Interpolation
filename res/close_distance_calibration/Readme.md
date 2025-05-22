Image 2 was captured at a distance of 100 cm, while Image 1 was taken at 79 cm.

These additional calibration images were specifically acquired to support the 
short-distance measurement mode of the Basler Blaze ToF camera. When this mode is 
enabled, calibration data obtained using the long-distance setting becomes unreliable and 
ineffective, making dedicated short-range calibration essential.

Our calcaulated matrix:

ir_coeffs = {
    'H11': ( 1.09040,   -0.000234     ), 
    'H12': (-0.17168,    0.000011     ), 
    'H13': (165.02078,   0.00764      ),
    'H21': ( 0.04629,   -0.000133     ), 
    'H22': ( 0.89844,   -0.000019     ), 
    'H23': ( 74.10048,  -0.00217      ),
    'H31': ( 0.000176,  -0.00000061   ), 
    'H32': (-0.000598,   0.000000099  ), 
    'H33': ( 1.0,       -2.18e-12     )
}

rgb_coeffs = {
    'H11': ( 0.29816,    0.0000289    ), 
    'H12': (-0.04691,   -0.0000075    ), 
    'H13': (175.13348,  -0.00616      ),
    'H21': (-0.01343,    0.0000220    ), 
    'H22': ( 0.28601,    0.0000095    ), 
    'H23': (116.28422,  -0.01694      ),
    'H31': (-0.000068,   0.000000068  ), 
    'H32': (-0.000142,  -0.000000019  ), 
    'H33': ( 1.0,       -2.18e-12     )
}
