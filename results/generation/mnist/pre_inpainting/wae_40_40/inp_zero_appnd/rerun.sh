# 2021-05-17 01:51:51.320567
python train_wae_v2.py --experiment_name=wae_40_40/inp_zero_appnd --convar_type=naive --inpainter_type=zero --dataset mnist --num_epochs=20 --render_every 2 --wae_fc 40 --wae_lc 40 --dataset_root /home/mprzewiezlikowski/uj/.data --max_benchmark_batches=-1 --lr=4e-4 --batch_size=128 --wae_recon_loss mse --wae_bl 1 --mask_train_size 0 --mask_unknown_size 14 --mask_val_size 14 --convar_append_mask
