# 2021-02-27 22:32:43.386559
python train_wae.py --experiment_name=new_metrics/wae_8_8/inp_mfa_pretrained_inpainter_frozen --inpainter_type=mfa --inpainter_path ../../gmm_missing/models/mnist_28_28 --dataset mnist --num_epochs=10 --render_every 2 --wae_fc 8 --wae_lc 8
