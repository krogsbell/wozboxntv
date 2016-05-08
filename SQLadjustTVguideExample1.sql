firstchannel=DR1
UPDATE channels SET weight = weight + 1000 WHERE weight < 1000
UPDATE channels SET weight = 0 WHERE id = 'DR1.dk' COLLATE NOCASE
UPDATE channels SET weight = 1 WHERE id = 'DR2.dk' COLLATE NOCASE
UPDATE channels SET weight = 2 WHERE id = 'DR3.dk' COLLATE NOCASE
UPDATE channels SET weight = 3 WHERE id = 'DRK.dk' COLLATE NOCASE
UPDATE channels SET weight = 4 WHERE id = 'TV2.dk' COLLATE NOCASE
UPDATE channels SET weight = 5 WHERE id = 'TV2Charlie.dk' COLLATE NOCASE
UPDATE channels SET weight = 6 WHERE id = 'TV2fri.dk' COLLATE NOCASE
UPDATE channels SET weight = 7 WHERE id = 'TV3.dk' COLLATE NOCASE
UPDATE channels SET weight = 8 WHERE id = 'TV3Plus.dk' COLLATE NOCASE
UPDATE channels SET weight = 9 WHERE id = 'TV3Sport1.dk' COLLATE NOCASE
UPDATE channels SET weight = 10 WHERE id = 'TV3Sport2.dk' COLLATE NOCASE
UPDATE channels SET weight = 11 WHERE id = 'Eurosport.dk' COLLATE NOCASE
UPDATE channels SET weight = 12 WHERE id = 'Eurosport2.dk' COLLATE NOCASE
UPDATE channels SET weight = 13 WHERE id = '6eren.dk' COLLATE NOCASE
UPDATE channels SET visible = 0 WHERE weight > 0
UPDATE channels SET visible = 1 WHERE weight < 14

