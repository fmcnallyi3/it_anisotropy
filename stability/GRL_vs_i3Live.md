----------- GLR vs I3 -------------

Total i3live runs: 16499
Total GRL runs: 14298
Only in i3live: 3652

Runs in i3live but missing in GRL: 3652

Most common reasons for missing runs in GRL:
i3_i3:short          3173
i3_i3:failed         3108
i3_i3:test           527
i3_i3:lid            304
i3_i3:data not filtered 56
i3_i3:spoiled        33
i3_i3:set good end time 9
i3_i3:RC override: bad InIce 7
i3_i3:gap in filtered data 5
i3_i3:standard candle heater on 4
i3_i3:many zombie DOMs 2
i3_i3:GPS time errors 1
i3_i3:all trigger and filter rates off by large amounts 1
i3_i3:duplicate events reported 1
i3_i3:bad year in run metadata 1

Sample missing runs:
Run 120124 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120126 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120128 | i3 status: False | i3 reason: ['failed'] | 
Run 120129 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120130 | i3 status: False | i3 reason: ['failed', 'gap in filtered data'] | 
Run 120133 | i3 status: False | i3 reason: ['short', 'test', 'failed'] | 
Run 120134 | i3 status: False | i3 reason: ['short', 'test', 'failed'] | 
Run 120135 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120136 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120137 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120138 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120139 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120140 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120141 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120142 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120143 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120144 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120145 | i3 status: False | i3 reason: ['short', 'failed'] | 
Run 120147 | i3 status: False | i3 reason: ['short', 'test', 'failed'] | 
Run 120148 | i3 status: False | i3 reason: ['short', 'test', 'failed'] | 

Mismatch counts (good in one, bad in other):  1272

Runs that are bad in i3 and good in GLR 1272

Runs that are good in i3 and bad in GLR 0

Most common reasons:
grl:short            908
grl:domcal           203
i3:set good end time 83
grl:it               68
i3:RC override: good IceTop 63
grl:partial          62
grl:has              31
grl:lost             31
grl:bad              24
grl:manually.        22
i3:blessed           22
grl:validated        21
grl:dc               19
grl:the              17
grl:files.           15

Sample mismatches:
Run 120163 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120169 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120192 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120193 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120217 | GRL good: False | i3 good: True | GRL reason: ['noicetop'] | i3 reason: []
Run 120231 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120258 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120336 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120349 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120445 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120446 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120487 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120488 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120489 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120491 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120492 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120500 | GRL good: False | i3 good: True | GRL reason: ['short'] | i3 reason: []
Run 120563 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120564 | GRL good: False | i3 good: True | GRL reason: ['domcal'] | i3 reason: []
Run 120579 | GRL good: False | i3 good: True | GRL reason: ['partial', 'it'] | i3 reason: []