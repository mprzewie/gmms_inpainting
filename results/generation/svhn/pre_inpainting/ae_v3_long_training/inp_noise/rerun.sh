# 2021-05-21 03:09:29.259063
python train_wae_v2.py --experiment_name=ae_v3_long_training/inp_noise --convar_type=naive --inpainter_type=noise --batch_size 64 --dataset svhn --img_size 32 --mask_train_size 0 --mask_unknown_size 16 --mask_val_size 16 --num_epochs=50 --render_every 2 --dataset_root /mnt/users/mprzewiezlikowski/local/data/.data/ --lr 2e-4 --wae_disc_loss_weight 0 --skip_fid --wae_recon_loss mse --wae_bl 2 --wae_depth 2 --max_benchmark_batches -1 --wae_latent_size 60 --wae_fc 32 --wae_lc 96
