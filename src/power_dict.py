import numpy as np
import config

#入れ子のdict型で各波長，各target_powerにおけるNDフィルターの場所を持っておく．
#近傍taraget_wavelength，近傍target_powerにおけるNDフィルターの位置にinitposで移動することでPIDパワー調整時間を減らす

class PowerDict:
    def __init__(self) -> None:
        self.power_dict = {}

    def add(self, target_wavelength:int, target_power:float, pos:int) -> None:
        if target_wavelength not in self.power_dict:
            self.power_dict[target_wavelength] = {}
        self.power_dict[target_wavelength][target_power] = pos

    def get_nearest(self, target_wavelength:int, target_power:float) -> int:
        try :
            if target_wavelength in self.power_dict:
                if target_power in self.power_dict[target_wavelength]:
                    return self.power_dict[target_wavelength][target_power]
                else:
                    target_power_list = list(self.power_dict[target_wavelength].keys())
                    nearest_target_power = target_power_list[np.argmin(np.abs(np.array(target_power_list) - target_power))]
                    return self.power_dict[target_wavelength][nearest_target_power]
            else:
                target_wavelength_list = list(self.power_dict.keys())
                nearest_target_wavelength = target_wavelength_list[np.argmin(np.abs(np.array(target_wavelength_list) - target_wavelength))]
                target_power_list = list(self.power_dict[nearest_target_wavelength].keys())
                nearest_target_power = target_power_list[np.argmin(np.abs(np.array(target_power_list) - target_power))]
                return self.power_dict[nearest_target_wavelength][nearest_target_power]
        except Exception as e:
            print(e)
            return config.NDINITPOS
        
if __name__ == '__main__':
    pd = PowerDict()
    print(pd.get_nearest(700, 0.1))
    pd.add(700, 0.1, 100)
    print(pd.get_nearest(700, 0.1))
    print(pd.get_nearest(701, 0.1))
    pd.add(701, 0.1, 200)
    print(pd.get_nearest(701, 0.1))
    print(pd.get_nearest(702, 0.1))