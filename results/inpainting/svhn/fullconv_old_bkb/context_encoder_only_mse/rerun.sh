# 2021-02-28 09:18:31.143417
python train_inpainter.py --experiment_name fullconv/context_encoder_only_mse --dataset svhn --img_size 32 --mask_hidden_w 16 --mask_hidden_h 16 --batch_size 64 --architecture fullconv --bkb_fc 32 --bkb_lc 32 --bkb_depth 3 --bkb_block_length 2 --num_factors 1 --a_amplitude 0.2 --num_epochs 100 --l_nll_weight 0 --l_mse_weight 1
