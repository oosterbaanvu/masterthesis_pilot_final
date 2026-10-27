import numpy as np
import pandas as pd
from thesis_pilot.controls import Controls

class Layers(Controls):
    """Expose hard, univariate, and conditional layers without changing historical B."""
    def score_layers(self, frame):
        hard, conditional = self.score(frame)
        statistical = hard.copy()
        for j, column in enumerate(self.targets):
            if self.contract[column]['type'] == 'numeric':
                v = pd.to_numeric(frame[column], errors='coerce').to_numpy(float)
                p = self.stats[column]
                statistical[:, j] |= (v < p['qlo']) | (v > p['qhi']) | (v < p['ilo']) | (v > p['ihi'])
            else:
                shares = frame[column].astype(str).map(self.stats[column]['shares']).fillna(0)
                statistical[:, j] |= shares.to_numpy() < .005
        assert np.all(~hard | statistical) and np.all(~statistical | conditional)
        return {'R': hard, 'RS': statistical, 'RSM': conditional}
