# 2021-05-21 15:41:10.520539
python train_wae_v2.py --experiment_name=ae_tryout/inp_noise --convar_type=naive --inpainter_type=noise --dataset mnist --mask_train_size 0 --mask_unknown_size 14 --mask_val_size 14 --num_epochs=25 --render_every 2 --wae_fc 8 --wae_lc 80 --dataset_root /home/mprzewiezlikowski/uj/.data --max_benchmark_batches=-1 --lr=2e-4 --batch_size=128 --wae_recon_loss mse --wae_bl 1 --wae_disc_loss_weight 0 --skip_fid
